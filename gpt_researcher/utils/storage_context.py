from dataclasses import dataclass as dc_dataclass
from dataclasses import field

from graphrag.index.cache.pipeline_cache import PipelineCache
from graphrag.index.storage.pipeline_storage import PipelineStorage
from typing import List

@dc_dataclass
class PipelineQueryStats:
    """Pipeline running stats."""

    query: str = field(default="")
    """Float representing the total runtime."""

    sub_queries: dict[str, List[str]] = field(default_factory=dict)
    """Number of documents."""

    queried_at: str = field(default="")


@dc_dataclass
class PipelineQueryWrapper:
    """Pipeline running stats."""

    queries: List[PipelineQueryStats] = field(default_factory=list)