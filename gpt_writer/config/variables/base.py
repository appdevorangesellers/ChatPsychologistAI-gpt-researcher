from typing import Union
from typing_extensions import TypedDict

class BaseConfig(TypedDict):
    SMART_LLM: str
    STRATEGIC_LLM: str
    SUBREPORT_TOTAL_WORDS: int
    REPORT_FORMAT: str
