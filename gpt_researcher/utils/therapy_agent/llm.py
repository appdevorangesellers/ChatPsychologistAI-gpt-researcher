from ..llm import construct_subtopics as general_construct_subtopics
from gpt_researcher.prompts.therapy_prompts import generate_therapies_prompt

async def construct_therapy_list(task: str, data: str, config, subtopics: list = []) -> list:
    from gpt_researcher.prompts import prompts
    prompts.generate_subtopics_prompt = generate_therapies_prompt
    return await general_construct_subtopics(task, data, config, subtopics)
