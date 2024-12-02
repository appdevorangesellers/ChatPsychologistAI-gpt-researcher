# libraries
from __future__ import annotations

import json
import logging
from typing import Optional, Any, Dict

from colorama import Fore, Style
from langchain.output_parsers import PydanticOutputParser
from langchain.prompts import PromptTemplate

from .costs import estimate_llm_cost
from .validators import Subtopics


def get_llm(llm_provider, **kwargs):
    from gpt_researcher.llm_provider import GenericLLMProvider
    return GenericLLMProvider.from_provider(llm_provider, **kwargs)


async def create_chat_completion(
        messages: list,  # type: ignore
        model: Optional[str] = None,
        temperature: Optional[float] = 0.4,
        max_tokens: Optional[int] = 4000,
        llm_provider: Optional[str] = None,
        stream: Optional[bool] = False,
        websocket: Any | None = None,
        llm_kwargs: Dict[str, Any] | None = None,
        cost_callback: callable = None
) -> str:
    """Create a chat completion using the OpenAI API
    Args:
        messages (list[dict[str, str]]): The messages to send to the chat completion
        model (str, optional): The model to use. Defaults to None.
        temperature (float, optional): The temperature to use. Defaults to 0.4.
        max_tokens (int, optional): The max tokens to use. Defaults to 4000.
        stream (bool, optional): Whether to stream the response. Defaults to False.
        llm_provider (str, optional): The LLM Provider to use.
        webocket (WebSocket): The websocket used in the currect request,
        cost_callback: Callback function for updating cost
    Returns:
        str: The response from the chat completion
    """
    # validate input
    if model is None:
        raise ValueError("Model cannot be None")
    if max_tokens is not None and max_tokens > 16001:
        raise ValueError(
            f"Max tokens cannot be more than 16,000, but got {max_tokens}")

    # Get the provider from supported providers
    provider = get_llm(llm_provider, model=model, temperature=temperature,
                       max_tokens=max_tokens, **(llm_kwargs or {}))

    response = ""
    # create response
    for _ in range(10):  # maximum of 10 attempts
        response = await provider.get_chat_response(
            messages, stream, websocket
        )

        if cost_callback:
            llm_costs = estimate_llm_cost(str(messages), response)
            cost_callback(llm_costs)

        return response

    logging.error(f"Failed to get response from {llm_provider} API")
    raise RuntimeError(f"Failed to get response from {llm_provider} API")