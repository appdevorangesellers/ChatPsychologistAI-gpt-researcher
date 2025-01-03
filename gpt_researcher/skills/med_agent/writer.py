from ...utils.med_agent.llm import construct_med_groups, construct_med_names
from ..writer import ReportGenerator
from gpt_researcher.actions.med_agent import generate_report

class MedReportGenerator(ReportGenerator):
    async def get_med_groups(self, query):
        """Retrieve med names for the research."""
        med_names = await construct_med_groups(
            task=query,
            data=self.researcher.context,
            config=self.researcher.cfg,
            subtopics=self.researcher.subtopics,
        )

        return med_names

    async def get_med_names(self, query):
        """Retrieve med names for the research."""
        med_names = await construct_med_names(
            task=query,
            data=self.researcher.context,
            config=self.researcher.cfg,
            subtopics=self.researcher.subtopics,
        )

        return med_names

    async def write_report(self, query, ext_context=None) -> str:
        from gpt_researcher import actions

        actions.generate_report = generate_report
        return await super(MedReportGenerator, self).write_report(query, ext_context)
