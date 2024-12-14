from .researcher import ResearchConductor
from ..actions.utils import stream_output
from ..actions.query_processing import plan_research_outline

class QuestionResearchConductor(ResearchConductor):

    def __init__(
        self,
        researcher,
    ):
        super(QuestionResearchConductor, self).__init__(researcher)
        self.max_search_results_per_query = 2

    async def plan_research(self, query):
        await stream_output(
            "logs",
            "planning_research",
            f"🤔 Planning the research strategy and subtasks (this may take a minute)...",
            self.researcher.websocket,
        )

        return await plan_research_outline(
            query='',
            type="question",
            search_results=query,
            cfg=self.researcher.cfg,
            cost_callback=self.researcher.add_costs,
        )