import asyncio
from typing import List, Dict, Any
from ..config.config import Config
from ..utils.llm import create_chat_completion
from ..utils.logger import get_formatted_logger
from gpt_researcher.prompts.prompts import (
    get_prompt,
    generate_report_introduction,
    get_prompt_by_report_type,
)
from gpt_researcher.prompts import prompts
from ..utils.enum import Tone, ReportType

logger = get_formatted_logger()

async def write_report_introduction(
    query: str,
    context: str,
    agent_role_prompt: str,
    config: Config,
    websocket=None,
    cost_callback: callable = None
) -> str:
    """
    Generate an introduction for the report.

    Args:
        query (str): The research query.
        context (str): Context for the report.
        role (str): The role of the agent.
        config (Config): Configuration object.
        websocket: WebSocket connection for streaming output.
        cost_callback (callable, optional): Callback for calculating LLM costs.

    Returns:
        str: The generated introduction.
    """

    print("write_report_introduction prompt", generate_report_introduction(query, context))
    #print(c)
    try:
        introduction = await create_chat_completion(
            model=config.smart_llm_model,
            messages=[
                {"role": "system", "content": f"{agent_role_prompt}"},
                {"role": "user", "content": generate_report_introduction(
                    query, context)},
            ],
            temperature=0.25,
            llm_provider=config.smart_llm_provider,
            stream=True,
            websocket=websocket,
            max_tokens=config.smart_token_limit,
            llm_kwargs=config.llm_kwargs,
            cost_callback=cost_callback,
        )
        return introduction
    except Exception as e:
        logger.error(f"Error in generating report introduction: {e}")
    return ""

async def generate_report(
    query: str,
    context,
    agent_role_prompt: str,
    tone: Tone,
    websocket,
    cfg,
    cost_callback: callable = None,
    report_type: str = ReportType.ResearchReport.value,
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
    #generate_prompt = get_prompt()
    generate_prompt = prompts.get_prompt_by_report_type(report_type)
    report = ""

    if report_type == "subtopic_report":
        content = f"{generate_prompt(query, context, report_format=cfg.report_format, tone=tone, total_words=cfg.subreport_total_words, language=cfg.language)}"
    else:
        content = f"{generate_prompt(query, context, report_format=cfg.report_format, tone=tone, total_words=cfg.total_words)}"

    print("generate_report prompt", content)
    #print(c)

    try:
        print("cfg.smart_llm_provider", cfg.smart_llm_provider)
        print("cfg.smart_llm_model", cfg.smart_llm_model)

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
