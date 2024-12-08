# Copyright (c) 2024 Microsoft Corporation.
# Licensed under the MIT License

"""The GlobalSearch Implementation."""

import asyncio
import json
import logging
import time
from collections.abc import AsyncGenerator
from dataclasses import dataclass
from typing import Any

import pandas as pd
import tiktoken

from graphrag.callbacks.global_search_callbacks import GlobalSearchLLMCallback
from graphrag.llm.openai.utils import try_parse_json_object
from graphrag.prompts.query.global_search_knowledge_system_prompt import (
    GENERAL_KNOWLEDGE_INSTRUCTION,
)
from graphrag.prompts.query.global_search_map_system_prompt import (
    MAP_SYSTEM_PROMPT,
)
from graphrag.prompts.query.global_search_reduce_system_prompt import (
    NO_DATA_ANSWER,
    REDUCE_SYSTEM_PROMPT,
)
from graphrag.query.context_builder.builders import GlobalContextBuilder
from graphrag.query.context_builder.conversation_history import (
    ConversationHistory,
)
from graphrag.query.llm.base import BaseLLM
from graphrag.query.llm.text_utils import num_tokens
from graphrag.query.structured_search.base import BaseSearch, SearchResult
from graphrag.query.structured_search.global_search.search import GlobalSearch

DEFAULT_MAP_LLM_PARAMS = {
    "max_tokens": 1000,
    "temperature": 0.0,
}

DEFAULT_REDUCE_LLM_PARAMS = {
    "max_tokens": 2000,
    "temperature": 0.0,
}

log = logging.getLogger(__name__)


@dataclass(kw_only=True)
class GlobalExtractResult():
    """A GlobalSearch result."""

    response: str | dict[str, Any] | list[dict[str, Any]]
    context_data: str | list[pd.DataFrame] | dict[str, pd.DataFrame]

class GlobalExtract(GlobalSearch):
    async def asearch(
        self,
        query: str,
        conversation_history: ConversationHistory | None = None,
        **kwargs: Any,
    ) -> GlobalExtractResult:
        """
        Perform a global search.

        Global search mode includes two steps:

        - Step 1: Run parallel LLM calls on communities' short summaries to generate answer for each batch
        - Step 2: Combine the answers from step 2 to generate the final answer
        """
        # Step 1: Generate answers for each batch of community short summaries
        llm_calls, prompt_tokens, output_tokens = {}, {}, {}

        start_time = time.time()
        sub_queries = query.split('\\n')
        print("sub_queries", sub_queries)
        context_result = await asyncio.gather(*[
            self.context_builder.build_context(
                query=sub_query,
                conversation_history=conversation_history,
                **self.context_builder_params,
            )
            for sub_query in sub_queries
        ])
        print("context_result", context_result)
        print(c)

        context_result = await self.context_builder.build_context(
            query=query,
            conversation_history=conversation_history,
            **self.context_builder_params,
        )
        llm_calls["build_context"] = context_result.llm_calls
        prompt_tokens["build_context"] = context_result.prompt_tokens
        output_tokens["build_context"] = context_result.output_tokens

        if self.callbacks:
            for callback in self.callbacks:
                callback.on_map_response_start(context_result.context_chunks)  # type: ignore
        #print('context_result.context_chunks', context_result.context_chunks)
        map_responses = await asyncio.gather(*[
            self._map_response_single_batch(
                context_data=data, query=query, **self.map_llm_params
            )
            for data in context_result.context_chunks
        ])
        if self.callbacks:
            for callback in self.callbacks:
                callback.on_map_response_end(map_responses)
        llm_calls["map"] = sum(response.llm_calls for response in map_responses)
        prompt_tokens["map"] = sum(response.prompt_tokens for response in map_responses)
        output_tokens["map"] = sum(response.output_tokens for response in map_responses)

        # Step 2: Combine the intermediate answers from step 2 to generate the final answer
        reduce_response = await self._reduce_response(
            map_responses=map_responses,
            query=query,
            **self.reduce_llm_params,
        )

        return GlobalExtractResult(
            context_data=reduce_response,
            response=''
        )

    async def _reduce_response(
        self,
        map_responses: list[SearchResult],
        query: str,
        **llm_kwargs,
    ):
        """Combine all intermediate responses from single batches into a final answer to the user query."""
        text_data = ""
        search_prompt = ""
        start_time = time.time()
        try:
            # collect all key points into a single list to prepare for sorting
            key_points = []
            for index, response in enumerate(map_responses):
                if not isinstance(response.response, list):
                    continue
                for element in response.response:
                    if not isinstance(element, dict):
                        continue
                    if "answer" not in element or "score" not in element:
                        continue
                    key_points.append({
                        "analyst": index,
                        "answer": element["answer"],
                        "score": element["score"],
                    })

            # filter response with score = 0 and rank responses by descending order of score
            filtered_key_points = [
                point
                for point in key_points
                if point["score"] > 0  # type: ignore
            ]

            if len(filtered_key_points) == 0 and not self.allow_general_knowledge:
                # return no data answer if no key points are found
                log.warning(
                    "Warning: All map responses have score 0 (i.e., no relevant information found from the dataset), returning a canned 'I do not know' answer. You can try enabling `allow_general_knowledge` to encourage the LLM to incorporate relevant general knowledge, at the risk of increasing hallucinations."
                )
                return SearchResult(
                    response=NO_DATA_ANSWER,
                    context_data="",
                    context_text="",
                    completion_time=time.time() - start_time,
                    llm_calls=0,
                    prompt_tokens=0,
                    output_tokens=0,
                )

            filtered_key_points = sorted(
                filtered_key_points,
                key=lambda x: x["score"],  # type: ignore
                reverse=True,  # type: ignore
            )

            data = []
            total_tokens = 0
            for point in filtered_key_points:
                formatted_response_data = []
                formatted_response_data.append(
                    f'----Analyst {point["analyst"] + 1}----'
                )
                formatted_response_data.append(
                    f'Importance Score: {point["score"]}'  # type: ignore
                )
                formatted_response_data.append(point["answer"])  # type: ignore
                formatted_response_text = "\n".join(formatted_response_data)
                if (
                    total_tokens
                    + num_tokens(formatted_response_text, self.token_encoder)
                    > self.max_data_tokens
                ):
                    break
                data.append(formatted_response_text)
                total_tokens += num_tokens(formatted_response_text, self.token_encoder)
            text_data = "\n\n".join(data)

            '''search_prompt = self.reduce_system_prompt.format(
                report_data=text_data, response_type=self.response_type
            )'''

            # ChatPsy
            #print("search_prompt", search_prompt)
            #print(c)

            return text_data
        except Exception:
            log.exception("Exception in reduce_response")
            return text_data
