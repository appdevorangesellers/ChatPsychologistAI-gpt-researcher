from gpt_researcher.utils.enum import Tone, ReportType
from datetime import date, datetime, timezone
import warnings

def generate_symptom_summary_report_prompt(
    topic: str,
    context,
    report_format="apa",
    total_words=1000,
    tone=None,
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
Using the latest information available, construct detailed summaries about topic: {topic}.
Provide consistent discipline' based on the articles’ context.
The report should mainly focus on the mentioned {topic}. 
Each {topic}'s summary should be well structured, informative, in-depth, and comprehensive, with facts and numbers if available. The report totally should be at least {total_words} words.
You should strive to write the report with all details related to {topic}.

Please follow all of the following guidelines in your report:
- You MUST determine your own concrete and valid opinion based on the given reports. Do NOT defer to general and meaningless conclusions. If you don't know the answer, just say so. Do not make anything up.
- You MUST write the summary with markdown syntax and {report_format.upper()} format.
- You MUST prioritize the relevance, reliability, and significance of the sources you use. Choose trusted sources over less reliable ones.
- You must also prioritize new articles over older articles if the source can be trusted.
- Use in-text citation references in {report_format.upper()} format and make it with markdown hyperlink placed at the end of the sentence or paragraph that references them like this: ([in-text citation](url)).
- {reference_prompt}
- {tone_prompt}
- The response may also include relevant real-world knowledge outside the dataset, but it must be explicitly annotated with a verification tag [LLM: verify]. For example: "This is an example sentence supported by real-world knowledge [LLM: verify]."
- Add sections and commentary to the response as appropriate for the length and format. Style the response in markdown.

Please do your best, this is very important to my career.
Assume that the current date is {date.today()}.
"""

report_type_mapping = {
    ReportType.ResearchReport.value: generate_symptom_summary_report_prompt,
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