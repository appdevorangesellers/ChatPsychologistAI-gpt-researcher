import warnings
from datetime import date, datetime, timezone

from .utils.enum import Tone
from typing import List, Dict, Any

def generate_search_queries_prompt(
    question: str,
    max_iterations: int = 3,
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

    task = question
    context_prompt = f"""
You are a seasoned research assistant tasked with generating search queries to find relevant information for the following task: "{task}".
Context: {context}

Use this context to inform and refine your search queries. The context provides real-time web information that can help you generate more specific and relevant queries. Consider any current events, recent developments, or specific details mentioned in the context that could enhance the search queries.
""" if context else f"""
You are a seasoned research assistant tasked with generating search queries to clarify relation of topics, that have critical points, with mental health and disorders for the subject.
The queries are essential in providing insightful knowledge about making mental health diagnoses for the subject.

Considering the importance of the queries to inform and refine your search queries.
"""


    dynamic_example = ", ".join([f'"query {i+1}"' for i in range(max_iterations)])
    dynamic_example += ", ..." if max_iterations > 1 else ""
    return f"""Write search queries to search online that form an objective understanding of the mental health from the subject's data: "{task}"

Assume the current date is {datetime.now(timezone.utc).strftime('%B %d, %Y')} if required.

{context_prompt}
You must respond with a list of strings in the following format: [{dynamic_example}].
The response should contain ONLY the list.
"""

def generate_search_queries_prompt_backup(
    question: str,
    max_iterations: int = 3,
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

    task = question

    context_prompt = f"""
You are a seasoned research assistant tasked with generating search queries to find relevant information for the following task: "{task}".
Context: {context}

Use this context to inform and refine your search queries. The context provides real-time web information that can help you generate more specific and relevant queries. Consider any current events, recent developments, or specific details mentioned in the context that could enhance the search queries.
""" if context else ""

    dynamic_example = ", ".join([f'"query {i+1}"' for i in range(max_iterations)])

    return f"""Write {max_iterations} google search queries to search online that form an objective opinion from the following task: "{task}"

Assume the current date is {datetime.now(timezone.utc).strftime('%B %d, %Y')} if required.

{context_prompt}
You must respond with a list of strings in the following format: [{dynamic_example}].
The response should contain ONLY the list.
"""


def generate_report_prompt(
    question: str,
    context,
    report_format="apa",
    total_words=1000,
    tone=None,
):
    """Generates the report prompt for the given question and research summary.
    Args: question (str): The question to generate the report prompt for
            research_summary (str): The research summary to generate the report prompt for
    Returns: str: The report prompt for the given question and research summary
    """

    reference_prompt = f"""
Points supported by data should list their data references as follows:

"This is an example sentence supported by multiple data references [Data: <dataset name> (record ids); <dataset name> (record ids)]."

Do not list more than 5 record ids in a single reference. Instead, list the top 5 most relevant record ids and add "+more" to indicate that there are more.

For example:

"Person X is the owner of Company Y and subject to many allegations of wrongdoing [Data: Sources (15, 16), Reports (1), Entities (5, 7); Relationships (23); Claims (2, 7, 34, 46, 64, +more)]."

where 15, 16, 1, 5, 7, 23, 2, 7, 34, 46, and 64 represent the id (not the index) of the relevant data record.

Do not include information where the supporting evidence for it is not provided.
"""

    tone_prompt = f"Write the report in a {tone.value} tone." if tone else ""

    return f"""
Analyst Reports: "{context}"
---
Mental data: "{question}"
---
Using the above reports which focused on different topics with critical points, conduct a comprehensive psychological analysis and research based on the subject's mental data to reduce short summaries about mental health and to diagnose mental disorders in details.
The report should dedicate one section for mental diagnoses along with detailed explanation for the diagnoses, since this part is the most crucial part of the report. If you can't diagnose any disorder, just say so. Do not make anything up.
The report should focus on the end-goal of the query, should be well structured, informative, 
in-depth, and comprehensive, with facts and numbers if available and at least {total_words} words.
You should strive to write the the report as detailed as you can using all relevant and necessary information provided.

Please follow all of the following guidelines in your report:
- You MUST determine your own concrete and valid opinion based on the given reports. Do NOT defer to general and meaningless conclusions. If you don't know the answer, just say so. Do not make anything up.
- You MUST write the summary with markdown syntax and {report_format} format.
- You MUST prioritize the relevance, reliability, and significance of the sources you use. Choose trusted sources over less reliable ones.
- You must also prioritize new articles over older articles if the source can be trusted.
- {reference_prompt}
- {tone_prompt}
- Add sections and commentary to the response as appropriate for the length and format. Style the response in markdown.

The response may also include relevant real-world knowledge outside the dataset, but it must be explicitly annotated with a verification tag [LLM: verify]. For example:
"This is an example sentence supported by real-world knowledge [LLM: verify]."

Please do your best, this is very important to my career.
Assume that the current date is {date.today()}.
"""


def get_report():
    return generate_report_prompt

def get_prompt():
    prompt_by_type = generate_report_prompt
    return prompt_by_type

