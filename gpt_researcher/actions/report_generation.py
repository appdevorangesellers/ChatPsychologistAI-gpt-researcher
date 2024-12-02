import asyncio
from typing import List, Dict, Any
from ..config.config import Config
from ..utils.llm import create_chat_completion
from ..utils.logger import get_formatted_logger
from ..prompts import (
    get_prompt,
)
from ..utils.enum import Tone

logger = get_formatted_logger()

async def generate_report(
    query: str,
    context,
    agent_role_prompt: str,
    tone: Tone,
    websocket,
    cfg,
    cost_callback: callable = None,
):
    """
    generates the final report
    Args:
        query:
        context:
        agent_role_prompt:
        report_type:
        websocket:
        tone:
        cfg:
        main_topic:
        existing_headers:
        relevant_written_contents:
        cost_callback:

    Returns:
        report:

    """
    generate_prompt = get_prompt()
    report = ""

    content = f"{generate_prompt(query, context, report_format=cfg.report_format, tone=tone, total_words=cfg.total_words)}"

    print("generate_report prompt", content)
    # print(c)

    try:
        report = await create_chat_completion(
            model=cfg.smart_llm_model,
            messages=[
                {"role": "system", "content": f"{agent_role_prompt}"},
                {"role": "user", "content": content},
            ],
            temperature=0.35,
            llm_provider=cfg.smart_llm_provider,
            stream=True,
            websocket=websocket,
            max_tokens=cfg.smart_token_limit,
            llm_kwargs=cfg.llm_kwargs,
            cost_callback=cost_callback,
        )
    except Exception as e:
        print(f"Error in generate_report: {e}")

    return report
