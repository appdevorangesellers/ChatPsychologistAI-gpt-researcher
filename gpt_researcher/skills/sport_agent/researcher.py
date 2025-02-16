from gpt_researcher.skills.researcher import ResearchConductor
from gpt_researcher.actions.utils import stream_output
from gpt_researcher.actions.query_processing import get_search_results

class SportResearchConductor(ResearchConductor):

    def __init__(
        self,
        researcher,
    ):
        super(SportResearchConductor, self).__init__(researcher)
        self.retriever_include_raw_content = True
        self.max_search_results_per_query = 2

    async def generate_summary(self, sub_query, search_results):
        return ''

    async def _generate_files(self, content, title):
        return ''

    async def plan_research(self, query):
        print("SportResearchConductor plan_research")
        return [query]