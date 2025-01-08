from ...utils.therapy_agent.llm import construct_therapy_list
from ..writer import ReportGenerator
from gpt_researcher.actions.med_agent import generate_report

class TherapyReportGenerator(ReportGenerator):
    async def get_therapy_list(self, query):
        """Retrieve med names for the research."""
        med_names = await construct_therapy_list(
            task=query,
            data=self.researcher.context,
            config=self.researcher.cfg,
            subtopics=self.researcher.subtopics,
        )

        return med_names

    async def write_report(self, query, ext_context=None) -> str:
        from gpt_researcher import actions

        actions.generate_report = generate_report
        return await super(TherapyReportGenerator, self).write_report(query, ext_context)
