import warnings
from datetime import date, datetime, timezone

from gpt_researcher.utils.enum import Tone, ReportType
from typing import List, Dict, Any

def general_med_prompt(
    as_group: bool = False
):
    subtopic_type = "Subtopics must be specific medication names, must not be group or class of medications."
    subtopic_desc = """medications in {task}"""
    if as_group:
        subtopic_type = "Medications/subtopics should be a concise summary, grouped according to similarity and use broader terms."
        subtopic_desc = """{task}"""

    return """
Provided the main topic:

{task}

and research data:

{data}

- Construct a list of {task} which indicate the subtopics of a report document to be generated on the task. 
- These are a possible list of subtopics : {subtopics}.
- No limit for the number of subtopics. All {task} mentioned in the research data must be listed.
- There should NOT be any duplicate subtopics. """ + subtopic_type + """


"IMPORTANT!":
- Every {task} MUST be relevant to provided research data ONLY!

{format_instructions}
"""

def general_med_group_report_prompt(
    current_subtopic,
    context,
    report_format: str = "apa",
    max_subsections=5,
    total_words=800,
    tone: Tone = Tone.Objective,
    language: str = "english",
):
    return general_med_report_prompt(current_subtopic, context, report_format, max_subsections, total_words, tone, language, as_group=True)

def general_med_report_prompt(
    current_subtopic,
    context,
    report_format: str = "apa",
    max_subsections=5,
    total_words=800,
    tone: Tone = Tone.Objective,
    language: str = "english",
):
    return general_med_report_prompt(current_subtopic, context, report_format, max_subsections, total_words, tone, language, as_group=False)

def general_med_report_prompt(
    current_subtopic,
    context,
    report_format: str = "apa",
    max_subsections=5,
    total_words=800,
    tone: Tone = Tone.Objective,
    language: str = "english",
    as_group: bool = False
):

    headings = ['medication brand names', 'side effects']
    if as_group:
        headings = []

    return f"""
Context:
"{context}"

Main Topic and Subtopic:
Using the latest information available, construct a concise report on the subtopic: {current_subtopic}.
These are a possible list of headings: {headings}.
Include all factual information such as numbers, stats, quotes, etc if available. 

Content Focus:
- The report should focus on answering the question, be well-structured, informative, in-depth, and include facts and numbers if available.
- Use markdown syntax and follow the {report_format.upper()} format.

"Structure and Formatting":
- As this sub-report will be part of a larger report, include only the main body divided into suitable subtopics without any introduction or conclusion section.

- You MUST include markdown hyperlinks to relevant source URLs wherever referenced in the report, for example:

    ### Section Header

    This is a sample text. ([url website](url))

- The response may also include relevant real-world knowledge outside the dataset, but it must be explicitly annotated with a verification tag [LLM: verify]. For example: "This is an example sentence supported by real-world knowledge [LLM: verify]."
- Use H2 for the main subtopic header (##) and H3 for subsections (###).
- Use smaller Markdown headers (e.g., H2 or H3) for content structure, avoiding the largest header (H1) as it will be used for the larger report's heading.
- Organize your content into distinct sections/headings that complement but do not overlap with each other.

"Date":
Assume the current date is {datetime.now(timezone.utc).strftime('%B %d, %Y')} if required.

"IMPORTANT!":
- You MUST write the report in the following language: {language}.
- The focus MUST be on the topic! You MUST Leave out any information un-related to it!
- Must NOT have any introduction, conclusion, summary or reference section.
- You MUST include hyperlinks with markdown syntax ([url website](url)) related to the sentences wherever necessary.
- You MUST include hyperlinks with markdown syntax ([LLM: verify]) to real-world knowledge outside the dataset applied in the report. For example: "This is an example sentence supported by real-world knowledge [LLM: verify]."
- The report should have a minimum length of {total_words} words.
- Use an {tone.value} tone throughout the report.
- Preferable content of each heading is listed with bullets for the report to be easy to read.

Do NOT add a conclusion section.
"""

report_type_mapping = {
    ReportType.ResearchReport.value: general_med_group_report_prompt,
    ReportType.SubtopicReport.value: general_med_report_prompt,
}

def get_prompt_by_report_type(report_type):
    prompt_by_type = report_type_mapping.get(report_type)
    default_report_type = ReportType.ResearchReport.value
    if not prompt_by_type:
        warnings.warn(
            f"Invalid report type: {report_type}.\n"
            f"Please use one of the following: {', '.join([enum_value for enum_value in report_type_mapping.keys()])}\n"
            f"Using default report type: {default_report_type} prompt.",
            UserWarning,
        )
        prompt_by_type = report_type_mapping.get(default_report_type)
    return prompt_by_type