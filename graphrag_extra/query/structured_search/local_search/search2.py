# Copyright (c) 2024 Microsoft Corporation.
# Licensed under the MIT License

"""LocalSearch implementation."""

import logging
import time
from collections.abc import AsyncGenerator
from typing import Any

import tiktoken

from graphrag.prompts.query.local_search_system_prompt import (
    LOCAL_SEARCH_SYSTEM_PROMPT,
)
from graphrag.query.context_builder.builders import LocalContextBuilder
from graphrag.query.context_builder.conversation_history import (
    ConversationHistory,
)
from graphrag.query.llm.base import BaseLLM, BaseLLMCallback
from graphrag.query.llm.text_utils import num_tokens
from graphrag.query.structured_search.base import BaseSearch, SearchResult
from graphrag.query.structured_search.local_search.search import LocalSearch
import pandas as pd
from dataclasses import dataclass

DEFAULT_LLM_PARAMS = {
    "max_tokens": 1500,
    "temperature": 0.0,
}

log = logging.getLogger(__name__)

@dataclass(kw_only=True)
class LocalExtractResult():
    """A GlobalSearch result."""

    response: str | dict[str, Any] | list[dict[str, Any]]
    context_data: str | list[pd.DataFrame] | dict[str, pd.DataFrame]

class LocalExtract(LocalSearch):
    async def asearch(
        self,
        query: str,
        conversation_history: ConversationHistory | None = None,
        **kwargs,
    ) -> SearchResult:
        """Build local search context that fits a single context window and generate answer for the user query."""
        start_time = time.time()

        sub_queries = query.split(';')
        #print("sub_queries", sub_queries)

        '''context_results = [
            self.context_builder.build_context(
                query=sub_query,
                conversation_history=conversation_history,
                **kwargs,
                **self.context_builder_params,
            )
            for sub_query in sub_queries
        ]
        print("context_result LocalExtract context_records", [
            r.context_records
            for r in context_results
        ])
        print(c)'''

        summaries = []

        #for q in sub_queries:
        for q in query:
            if len(q.strip()) == 0: continue
            q = f"What potential mental health issues/disorders stand out from data: {q}"
            search_prompt = ""
            llm_calls, prompt_tokens, output_tokens = {}, {}, {}
            context_result = self.context_builder.build_context(
                query=q,
                conversation_history=conversation_history,
                **kwargs,
                **self.context_builder_params,
            )
            llm_calls["build_context"] = context_result.llm_calls
            prompt_tokens["build_context"] = context_result.prompt_tokens
            output_tokens["build_context"] = context_result.output_tokens

            log.info("GENERATE ANSWER: %s. QUERY: %s", start_time, query)
            try:
                if "drift_query" in kwargs:
                    drift_query = kwargs["drift_query"]
                    search_prompt = self.system_prompt.format(
                        context_data=context_result.context_chunks,
                        response_type=self.response_type,
                        global_query=drift_query,
                    )
                else:
                    search_prompt = self.system_prompt.format(
                        context_data=context_result.context_chunks,
                        response_type=self.response_type,
                    )
                search_messages = [
                    {"role": "system", "content": search_prompt},
                    {"role": "user", "content": q},
                ]

                response = await self.llm.agenerate(
                    messages=search_messages,
                    streaming=True,
                    callbacks=self.callbacks,
                    **self.llm_params,
                )

                print('response', response)

                formatted_response_data = []
                formatted_response_data.append(
                    f'##{q}'
                )
                formatted_response_data.append(response)  # type: ignore
                formatted_response_text = "\n".join(formatted_response_data)

                summaries.append(formatted_response_text)

                llm_calls["response"] = 1
                prompt_tokens["response"] = num_tokens(search_prompt, self.token_encoder)
                output_tokens["response"] = num_tokens(response, self.token_encoder)
            except Exception:
                log.exception("Exception in _asearch")
                response = ""

        text_summaries= "\n\n".join(summaries)
        print("text_summaries", text_summaries)

        return LocalExtractResult(
                #response=response,
                response=text_summaries,
                context_data="",
            )