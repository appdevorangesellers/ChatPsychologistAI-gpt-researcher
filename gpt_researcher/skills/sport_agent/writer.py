from ..writer import ReportGenerator
from gpt_researcher.actions.sport_agent import generate_report

class SportReportGenerator(ReportGenerator):
    async def write_report(self, query, ext_context=None) -> str:
        from gpt_researcher import actions

        actions.generate_report = generate_report
        return await super(SportReportGenerator, self).write_report(query, ext_context)
