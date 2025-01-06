from gpt_researcher.skills.researcher import ResearchConductor
class DiagnoseResearchConductor(ResearchConductor):

    def __init__(
        self,
        researcher,
    ):
        super(DiagnoseResearchConductor, self).__init__(researcher)
        self.retriever_include_raw_content = True

    async def generate_summary(self, sub_query, search_results):
        return ''

    async def _generate_files(self, content, title):
        return ''

    async def plan_research(self, query):
        return [query]