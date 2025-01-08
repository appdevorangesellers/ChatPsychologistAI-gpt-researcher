from gpt_researcher.skills.researcher import ResearchConductor
class DisorderResearchConductor(ResearchConductor):

    def __init__(
        self,
        researcher,
    ):
        super(DisorderResearchConductor, self).__init__(researcher)
        self.retriever_include_raw_content = True
        self.max_search_results_per_query = 5

    async def generate_summary(self, sub_query, search_results):
        return ''

    async def _generate_files(self, content, title):
        return ''

    async def plan_research(self, query):
        return [query]