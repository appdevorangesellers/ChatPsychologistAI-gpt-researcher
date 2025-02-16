from ...utils.symptom_agent.llm import construct_symptom_list
from ..writer import ReportGenerator
from gpt_researcher.actions.symptom_agent import generate_report

class SymptomReportGenerator(ReportGenerator):
    async def get_symptom_list(self, query):
        """Retrieve symptoms for the research."""
        symptoms = await construct_symptom_list(
            task=query,
            data=self.researcher.context,
            config=self.researcher.cfg,
            subtopics=self.researcher.subtopics,
        )

        return symptoms

    async def write_report(self, query, ext_context=None) -> str:
        from gpt_researcher import actions

        actions.generate_report = generate_report
        return await super(SymptomReportGenerator, self).write_report(query, ext_context)
