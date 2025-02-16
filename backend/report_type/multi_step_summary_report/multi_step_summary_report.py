import asyncio
from typing import List, Dict, Set, Optional, Any
from fastapi import WebSocket

from gpt_researcher import GPTMedResearcher as GPTResearcher
from gpt_researcher.actions import (
    generate_files,
)

class MSSummaryReport:
    def __init__(
        self,
        disorder: str,
        #report_type: str,
        #report_source: str,
        source_urls: List[str] = [],
        #document_urls: List[str] = [],
        #config_path: str = None,
        #tone: Any = "",
        #websocket: WebSocket = None,
        #subtopics: List[Dict] = [],
        #headers: Optional[Dict] = None
    ):
        self.disorder = disorder
        #self.report_type = report_type
        #self.report_source = report_source
        self.source_urls = source_urls
        #self.document_urls = document_urls
        #self.config_path = config_path
        #self.tone = tone
        #self.websocket = websocket
        #self.subtopics = subtopics
        #self.headers = headers or {}

        self.gpt_researcher = GPTResearcher(disorder=disorder)
        #self.existing_headers: List[Dict] = []
        #self.global_context: List[str] = []
        #self.global_written_sections: List[str] = []
        self.global_urls: Set[str] = set(
            self.source_urls) if self.source_urls else set()

    async def run(self) -> str:
        await self._initial_research(f'medication used for {self.disorder}')
        med_groups = await self._get_med_groups()
        report_introduction = await self.gpt_researcher.write_introduction(f'medication used for {self.disorder}')
        print('report_introduction', report_introduction)
        _, report_body = await self._generate_med_group_reports(med_groups)
        report = await self._construct_detailed_report(f'medication used for {self.disorder}', report_introduction,
                                                       report_body)
        print('report', report)

        '''for topic in med_groups:
            await self._initial_research(f'{topic.get("task")} for {self.disorder}')
            n_subtopics = await self._get_med_names(f'{topic.get("task")} for {self.disorder}')
            report_introduction = await self.gpt_researcher.write_introduction(f'{topic.get("task")} for {self.disorder}')
            print('report_introduction', report_introduction)
            _, report_body = await self._generate_med_reports(n_subtopics)
            report = await self._construct_detailed_report(f'{topic.get("task")} for {self.disorder}', report_introduction, report_body)
            print('report', report)
            break'''
        #report_introduction = await self.gpt_researcher.write_introduction()
        #_, report_body = await self._generate_subtopic_reports(subtopics)
        #self.gpt_researcher.visited_urls.update(self.global_urls)
        #report = await self._construct_detailed_report(report_introduction, report_body)
        #return report

    async def _initial_research(self, query) -> None:
        await self.gpt_researcher.conduct_context_research(query)
        #self.global_context = self.gpt_researcher.context
        self.global_urls.update(self.gpt_researcher.visited_urls)

    async def _get_med_groups(self) -> List[Dict]:
        subtopics_data = await self.gpt_researcher.get_med_groups()

        all_subtopics = []
        if subtopics_data and subtopics_data.subtopics:
            for subtopic in subtopics_data.subtopics:
                all_subtopics.append({"task": subtopic.task})
        else:
            print(f"Unexpected subtopics data format: {subtopics_data}")

        print("all_subtopics", all_subtopics)
        return all_subtopics

    async def _get_med_names(self, query = None) -> List[Dict]:
        subtopics_data = await self.gpt_researcher.get_med_names(query)

        all_subtopics = []
        if subtopics_data and subtopics_data.subtopics:
            for subtopic in subtopics_data.subtopics:
                all_subtopics.append({"task": subtopic.task})
        else:
            print(f"Unexpected subtopics data format: {subtopics_data}")

        print("_get_all_subtopics_2", all_subtopics)
        return all_subtopics

    async def _generate_med_group_reports(self, subtopics: List[Dict]) -> tuple:
        subtopic_reports = []
        subtopics_report_body = ""

        for subtopic in subtopics:
            subtopic["task"] = f"{subtopic.get('task')} for {self.disorder}"
            result = await self._get_med_group_report(subtopic)
            if result["report"]:
                subtopic_reports.append(result)
                subtopics_report_body += f"\n\n\n{result['report']}"

        return subtopic_reports, subtopics_report_body

    async def _get_med_group_report(self, subtopic: Dict) -> Dict[str, str]:
        current_subtopic_task = subtopic.get("task")

        subtopic_report = await self.gpt_researcher.write_med_report(f'{current_subtopic_task}')

        return {"topic": subtopic, "report": subtopic_report}

    async def _generate_med_reports(self, subtopics: List[Dict]) -> tuple:
        subtopic_reports = []
        subtopics_report_body = ""

        for subtopic in subtopics:
            result = await self._get_med_report(subtopic)
            if result["report"]:
                subtopic_reports.append(result)
                subtopics_report_body += f"\n\n\n{result['report']}"

        return subtopic_reports, subtopics_report_body

    async def _get_med_report(self, subtopic: Dict) -> Dict[str, str]:
        current_subtopic_task = subtopic.get("task")
        subtopic_assistant = GPTResearcher(report_type="subtopic_report")

        #subtopic_assistant.context = list(set(self.global_context))
        await subtopic_assistant.conduct_context_research(f'{current_subtopic_task} medication')
        self.global_urls.update(subtopic_assistant.visited_urls)

        #draft_section_titles = await subtopic_assistant.get_draft_section_titles(current_subtopic_task)

        #if not isinstance(draft_section_titles, str):
        #    draft_section_titles = str(draft_section_titles)

        #parse_draft_section_titles = self.gpt_researcher.extract_headers(draft_section_titles)
        #parse_draft_section_titles_text = [header.get(
        #    "text", "") for header in parse_draft_section_titles]

        #relevant_contents = await subtopic_assistant.get_similar_written_contents_by_draft_section_titles(
        #    current_subtopic_task, parse_draft_section_titles_text, self.global_written_sections
        #)

        subtopic_report = await subtopic_assistant.write_med_report(f'{current_subtopic_task}')

        #self.global_written_sections.extend(self.gpt_researcher.extract_sections(subtopic_report))
        #self.global_context = list(set(subtopic_assistant.context))
        #self.global_urls.update(subtopic_assistant.visited_urls)

        #self.existing_headers.append({
        #    "subtopic task": current_subtopic_task,
        #    "headers": self.gpt_researcher.extract_headers(subtopic_report),
        #})

        return {"topic": subtopic, "report": subtopic_report}

    async def _construct_detailed_report(self, title, introduction: str, report_body: str) -> str:
        toc = self.gpt_researcher.table_of_contents(report_body)
        #conclusion = await self.gpt_researcher.write_report_conclusion(report_body)
        conclusion_with_references = self.gpt_researcher.add_references(
            '', self.global_urls)
        report = f"{introduction}\n\n{toc}\n\n{report_body}\n\n{conclusion_with_references}"
        await generate_files(report, title)
        return report
