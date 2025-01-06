from ...utils.med_agent.llm import construct_med_groups, construct_med_names
from ..writer import ReportGenerator
from gpt_researcher.actions.diet_agent import generate_report

class DietReportGenerator(ReportGenerator):
    async def write_report(self, query, ext_context=None) -> str:
        from gpt_researcher import actions

        actions.generate_report = generate_report
        return await super(DietReportGenerator, self).write_report(query, ext_context)
