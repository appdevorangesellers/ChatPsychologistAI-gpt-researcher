from ...utils.enum import Tone, ReportType
from ..report_generation import generate_report as general_generate_report
from gpt_researcher.prompts.diagnose_prompts import get_prompt_by_report_type

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
    from gpt_researcher.prompts import prompts
    prompts.get_prompt_by_report_type = get_prompt_by_report_type

    return await general_generate_report(query, context, agent_role_prompt, tone, websocket, cfg, cost_callback, report_type)
