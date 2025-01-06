from gpt_researcher.utils.enum import Tone, ReportType
from datetime import date, datetime, timezone
import warnings
from . import prompts
from .prompts import get_prompt_by_report_type as general_get_prompt_by_report_type
def generate_summary_report_prompt(
    topic: str,
    context,
    report_format="apa",
    total_words=1000,
    tone=None,
    language: str = "english",
):
    reference_prompt = f"""
    You MUST write all used source urls at the end of the report as references, and make sure to not add duplicated sources, but only one reference for each.
    Every url should be hyperlinked: [url website](url)
    Additionally, you MUST include hyperlinks to the relevant URLs wherever they are referenced in the report: 

    eg: Author, A. A. (Year, Month Date). Title of web page. Website Name. [url website](url)
    """

    return f"""
Context: "{context}"
---
Using the latest information available, construct detailed report on the topic: {topic}.
These are a possible list of headings: ['diet with positive impact', 'diet with negative impact'].
Include all factual information such as numbers, stats, quotes, etc if available.

Content Focus:
- The report should focus on answering the question, be well-structured, informative, in-depth, and include facts and numbers if available.
- Use markdown syntax and follow the {report_format.upper()} format.

"Structure and Formatting":
- As this sub-report will be part of a larger report, include only the main body divided into suitable subtopics without any conclusion section.

- You MUST include markdown hyperlinks to relevant source URLs wherever referenced in the report, for example:

    ### Section Header

    This is a sample text. ([url website](url))

- The response may also include relevant real-world knowledge outside the dataset, but it must be explicitly annotated with a verification tag [LLM: verify]. For example: "This is an example sentence supported by real-world knowledge [LLM: verify]."
- Organize your content into distinct sections/headings that complement but do not overlap with each other.

"Date":
Assume the current date is {datetime.now(timezone.utc).strftime('%B %d, %Y')} if required.

"IMPORTANT!":
- You MUST write the report in the following language: {language}.
- The focus MUST be on the topic! You MUST Leave out any information un-related to it!
- Must NOT have any conclusion section.
- You MUST include hyperlinks with markdown syntax ([url website](url)) related to the sentences wherever necessary.
- You MUST include hyperlinks with markdown syntax ([LLM: verify]) to real-world knowledge outside the dataset applied in the report. For example: "This is an example sentence supported by real-world knowledge [LLM: verify]."
- The report should have a minimum length of {total_words} words.
- Use an {tone.value} tone throughout the report.
- {reference_prompt}
- Preferable content of each heading is listed with bullets for the report to be easy to read.

Do NOT add a conclusion section.
"""

report_type_mapping = {
    ReportType.ResearchReport.value: generate_summary_report_prompt,
}

def get_prompt_by_report_type(report_type):
    prompts.report_type_mapping = report_type_mapping
    return general_get_prompt_by_report_type(report_type)