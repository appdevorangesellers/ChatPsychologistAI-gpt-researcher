import asyncio
import json
import random

from ..actions.query_processing import plan_research_outline, get_search_results
from ..actions.utils import stream_output
from ..document import DocumentLoader
from ..actions import (
    generate_files,
)

from .researcher import ResearchConductor

class DataResearchConductor(ResearchConductor):
    async def plan_research(self, query):
        await stream_output(
            "logs",
            "planning_research",
            f"🤔 Planning the research strategy and subtasks (this may take a minute)...",
            self.researcher.websocket,
        )

        return await plan_research_outline(
            query=query,
            search_results=[],
            cfg=self.researcher.cfg,
            cost_callback=self.researcher.add_costs,
        )
