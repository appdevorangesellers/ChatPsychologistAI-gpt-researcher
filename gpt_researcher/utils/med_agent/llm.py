from ..llm import construct_subtopics as general_construct_subtopics
from gpt_researcher.prompts.med_prompts import general_med_prompt

async def construct_med_groups(task: str, data: str, config, subtopics: list = []) -> list:
    from gpt_researcher.prompts import prompts
    prompts.generate_subtopics_prompt = lambda: general_med_prompt(as_group=True)
    return await general_construct_subtopics(task, data, config, subtopics)

async def construct_med_names(task: str, data: str, config, subtopics: list = []) -> list:
    from gpt_researcher.prompts import prompts
    prompts.generate_subtopics_prompt = lambda: general_med_prompt(as_group=False)
    return await general_construct_subtopics(task, data, config, subtopics)
