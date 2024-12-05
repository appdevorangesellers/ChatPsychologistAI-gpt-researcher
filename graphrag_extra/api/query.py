from graphrag_extra.query.factories import (
    get_global_extract_engine,
)
from pydantic import validate_call
from graphrag.config.models.graph_rag_config import GraphRagConfig
import pandas as pd
from typing import Any

@validate_call(config={"arbitrary_types_allowed": True})
async def global_extract(
    config: GraphRagConfig,
    nodes: pd.DataFrame,
    entities: pd.DataFrame,
    communities: pd.DataFrame,
    community_reports: pd.DataFrame,
    community_level: int | None,
    dynamic_community_selection: bool,
    response_type: str,
    query: str,
) -> tuple[
    str | dict[str, Any] | list[dict[str, Any]],
    str | list[pd.DataFrame] | dict[str, pd.DataFrame],
]:
    from graphrag import api
    api.query.get_global_search_engine = get_global_extract_engine
    api.query._reformat_context_data = _reformat_context_data

    print('global_extract')
    return await api.query.global_search(
        config,
        nodes,
        entities,
        communities,
        community_reports,
        community_level,
        dynamic_community_selection,
        response_type,
        query
    )

def _reformat_context_data(context_data: dict|str) -> dict|str:
    return context_data