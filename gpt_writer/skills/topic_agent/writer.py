from gpt_researcher.skills.writer import ReportGenerator
from gpt_writer.actions.topic_agent import generate_report

class TopicReportGenerator(ReportGenerator):
    async def write_report(self, query, ext_context=None) -> str:
        from gpt_researcher import actions

        actions.generate_report = generate_report
        return await super(TopicReportGenerator, self).write_report(query, ext_context)
