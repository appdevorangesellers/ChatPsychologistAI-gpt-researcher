from gpt_researcher.config.variables.base import BaseConfig
from gpt_researcher.config.variables.default import DEFAULT_CONFIG as GPT_RESEARCHER_DEFAULT_CONFIG

DEFAULT_CONFIG: BaseConfig = {
    **GPT_RESEARCHER_DEFAULT_CONFIG,
    "SUBREPORT_TOTAL_WORDS": 200,
    "SMART_LLM": "google_genai:gemini-2.0-flash-exp",
    "STRATEGIC_LLM": "google_genai:gemini-2.0-flash-exp",
    "REPORT_FORMAT": "APA",
}
