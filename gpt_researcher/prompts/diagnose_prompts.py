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
    tone_prompt = f"Write the report in a {tone.value} tone." if tone else ""
    reference_prompt = f"""
    You MUST write all used source urls at the end of the report as references, and make sure to not add duplicated sources, but only one reference for each.
    Every url should be hyperlinked: [url website](url)
    Additionally, you MUST include hyperlinks to the relevant URLs wherever they are referenced in the report: 

    eg: Author, A. A. (Year, Month Date). Title of web page. Website Name. [url website](url)
    """

    return f"""
Context: "{context}"
---
Reduce detailed summaries about {topic}, and provide consistent discipline' based on the articles’ context.
The report should mainly focus on {topic}. Each diagnosis's summary should be well structured, informative, in-depth, and comprehensive, with facts and numbers if available. The report totally should be at least {total_words} words.
You should strive to write the report with all details related to the diagnoses for the mentioned disorder.

Please follow all of the following guidelines in your report:
- You MUST determine your own concrete and valid opinion based on the given reports. Do NOT defer to general and meaningless conclusions. If you don't know the answer, just say so. Do not make anything up.
- You MUST write the summary with markdown syntax and {report_format.upper()} format.
- You MUST prioritize the relevance, reliability, and significance of the sources you use. Choose trusted sources over less reliable ones.
- You must also prioritize new articles over older articles if the source can be trusted.
- Use in-text citation references in {report_format.upper()} format and make it with markdown hyperlink placed at the end of the sentence or paragraph that references them like this: (in-text citation).
- Don't forget to add a reference list at the end of the report in {report_format} format and full url links without hyperlinks.
- {reference_prompt}
- {tone_prompt}
- The response may also include relevant real-world knowledge outside the dataset, but it must be explicitly annotated with a verification tag [LLM: verify]. For example: "This is an example sentence supported by real-world knowledge [LLM: verify]."
- Add sections and commentary to the response as appropriate for the length and format. Style the response in markdown.

You MUST write the report in the following language: {language}.
Please do your best, this is very important to my career.
Assume that the current date is {date.today()}.
"""

report_type_mapping = {
    ReportType.ResearchReport.value: generate_summary_report_prompt,
}

def get_prompt_by_report_type(report_type):
    prompts.report_type_mapping = report_type_mapping
    return general_get_prompt_by_report_type(report_type)