from gpt_researcher.skills.researcher import ResearchConductor
class SymptomResearchConductor(ResearchConductor):

    def __init__(
        self,
        researcher,
    ):
        super(SymptomResearchConductor, self).__init__(researcher)
        self.retriever_include_raw_content = True

    async def generate_summary(self, sub_query, search_results):
        return ''

    async def _generate_files(self, content, title):
        return ''

    async def plan_research(self, query):
        return [f'symptoms related to {query}']