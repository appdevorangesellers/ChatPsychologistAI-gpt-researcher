import json_repair
from gpt_researcher.utils.llm import create_chat_completion
from ..prompts import generate_subtopic_key_discrepancy_prompt
from typing import Any, List, Dict
from ..config import Config
import logging

logger = logging.getLogger(__name__)

async def generate_subtopic_key_discrepancy(
    query: str,
    context: List[Dict[str, Any]],
    cfg: Config,
    cost_callback: callable = None
) -> List[str]:
    """
    Generate sub-queries using the specified LLM model.
    
    Args:
        query: The original query
        parent_query: The parent query
        report_type: The type of report
        max_iterations: Maximum number of research iterations
        context: Search results context
        cfg: Configuration object
        cost_callback: Callback for cost calculation
    
    Returns:
        A list of sub-queries
    """
    gen_queries_prompt = generate_subtopic_key_discrepancy_prompt(
        query,
        context=context
        # context=[]
    )

    print("gen_queries_prompt", gen_queries_prompt)
    # print(c)
    if not gen_queries_prompt:
        return []
    try:
        response = await create_chat_completion(
            model=cfg.strategic_llm_model,
            messages=[{"role": "user", "content": gen_queries_prompt}],
            temperature=1,
            llm_provider=cfg.strategic_llm_provider,
            max_tokens=None,
            llm_kwargs=cfg.llm_kwargs,
            cost_callback=cost_callback,
        )
    except Exception as e:
        logger.warning(f"Error with strategic LLM: {e}. Falling back to smart LLM.")
        response = await create_chat_completion(
            model=cfg.smart_llm_model,
            messages=[{"role": "user", "content": gen_queries_prompt}],
            temperature=cfg.temperature,
            max_tokens=cfg.smart_token_limit,
            llm_provider=cfg.smart_llm_provider,
            llm_kwargs=cfg.llm_kwargs,
            cost_callback=cost_callback,
        )

    print("generate_subtopic_key_discrepancy response", response)
    # print(c)

    #return json_repair.loads(response)
    return response