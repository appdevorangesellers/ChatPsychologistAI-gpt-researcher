from gpt_researcher.utils.enum import Tone, ReportType
from datetime import date, datetime, timezone
import warnings
from typing import List, Dict, Any
from . import prompts
from .prompts import get_prompt_by_report_type as general_get_prompt_by_report_type

def generate_subtopic_report_prompt(
    current_subtopic: str,
    context,
    report_format="apa",
    total_words=1000,
    tone=None,
    language: str = "english",
):
    return f"""
Context:
"{context}"

Main Topic and Subtopic:
Using the above information, construct a concise summary on the subtopic: {current_subtopic}.
Include all factual information such as numbers, stats, quotes, etc if available. 

Content Focus:
- The report should focus on answering the question, be well-structured, informative, in-depth, and include facts and numbers if available.

"Structure and Formatting":
- As this sub-report will be part of a larger report, construct a summary as concise as possible.

"Date":
Assume the current date is {datetime.now(timezone.utc).strftime('%B %d, %Y')} if required.

"IMPORTANT!":
- You MUST write the report in the following language: {language}.
- The focus MUST be on the topic! You MUST Leave out any information un-related to it!
- Must NOT have any introduction, conclusion or reference section.
- The report should have a minimum length of {total_words} words.
- Use an {tone.value} tone throughout the report.
- Preferable content of each heading is listed with bullets for the report to be easy to read.

Do NOT add a conclusion section.
"""

def generate_subtopic_key_discrepancy_prompt(
    current_subtopic: str,
    context: List[Dict[str, Any]] = [],
):
    """Generates the search queries prompt for the given question.
    Args:
        question (str): The question to generate the search queries prompt for
        parent_query (str): The main question (only relevant for detailed reports)
        report_type (str): The report type
        max_iterations (int): The maximum number of search queries to generate
        context (str): Context for better understanding of the task with realtime web information

    Returns: str: The search queries prompt for the given question
    """
    context_prompt = f"""
You are a psychologist about to make mental diagnoses based on this subject's mental data. You have to investigate whether the area is critical/negative for mental health and can lead to possible mental disorders.
Area: {current_subtopic}
Mental data: {context}
"""
    goal = f"""
Based on the provided mental data, describe the patient's {current_subtopic} in one short phrase focusing on the key discrepancy.
"""
    return f"""{goal}

Assume the current date is {datetime.now(timezone.utc).strftime('%B %d, %Y')} if required.

{context_prompt}
The response should contain only the short phrase focusing on the key discrepancy about Academic or Occupational Functioning, without any period or new space letter at the end.
"""

report_type_mapping = {
    ReportType.SubtopicReport.value: generate_subtopic_report_prompt,
}

def get_prompt_by_report_type(report_type):
    prompts.report_type_mapping = report_type_mapping
    return general_get_prompt_by_report_type(report_type)