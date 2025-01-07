from gpt_researcher import GPTSportResearcher, GPTSymptomResearcher
from colorama import Fore, Style
from .utils.views import print_agent_output
from typing import List, Dict, Set, Optional, Any
from gpt_researcher.actions import (
    generate_files,
)
import asyncio

class SportResearchAgent:
    def __init__(
        self,
        disorder: str
    ):
        self.disorder = disorder
        self.gpt_symptom_researcher = GPTSymptomResearcher(disorder=disorder)
        self.global_urls: Set[str] = set()

    async def research(self):
        await self.research_symptom()
        symptoms = await self._get_symptom_list()
        await self.construct_sport_report(symptoms)

    async def research_symptom(self):
        await self.gpt_symptom_researcher.conduct_research()
        report = await self.gpt_symptom_researcher.write_summary_report()
        await generate_files(report, f"{self.disorder} symptoms")

    async def _get_symptom_list(self) -> List[Dict]:
        subtopics_data = await self.gpt_symptom_researcher.get_symptom_list()

        all_subtopics = []
        if subtopics_data and subtopics_data.subtopics:
            for subtopic in subtopics_data.subtopics:
                all_subtopics.append({"task": subtopic.task})
        else:
            print(f"Unexpected subtopics data format: {subtopics_data}")

        print("all_subtopics", all_subtopics)
        return all_subtopics

    async def construct_sport_report(self, symptoms: List[Dict]):
        i = 1
        for topic in symptoms:
            topic_assistant = GPTSportResearcher(symptom=topic.get("task"))
            await topic_assistant.conduct_research()
            report = await topic_assistant.write_summary_report()
            await generate_files(report, f"{self.disorder} sport {topic.get('task')}")

            if i == 1: break
            i += 1
