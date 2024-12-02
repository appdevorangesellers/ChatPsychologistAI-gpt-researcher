from fastapi import WebSocket
from typing import Any
import json

from gpt_researcher import GPTResearcher


# from gpt_psychologist import GPTPsychologist


class BasicReport:
    def __init__(
            self,
            query: str,
            report_type: str,
            report_source: str,
            source_urls,
            tone: Any,
            config_path: str,
            websocket: WebSocket,
            headers=None
    ):
        self.query = query
        self.report_type = report_type
        self.report_source = report_source
        self.source_urls = source_urls
        self.tone = tone
        self.config_path = config_path
        self.websocket = websocket
        self.headers = headers or {}

    async def run(self):
        # Initialize researcher
        topics = [  # "Background",
            # "Developmental History",
            # "Motivation and Readiness for Change",
            "Substance Use (Drugs and Alcohol)",
            "Current Life Stressors",
            "Trauma and Past Experiences",
            # "Cognitive and Emotional Patterns",
            # "Cultural Background and Influences",
            # "Sleep and Rest Patterns"
        ]

        researcher = GPTResearcher(
            # query=self.query,
            # query=f"how {topic} relate to mental health",
            # report_type=self.report_type,
            # report_source=self.report_source,
            # source_urls=self.source_urls,
            tone=self.tone,
            config_path=self.config_path,
            websocket=self.websocket,
            # headers=self.headers
        )

        # topic = "Sleep and Rest Patterns"

        # Scrape data
        '''for topic in topics:
            #
            print("Topic: ", topic)
            await researcher.conduct_research(f"how {topic} relate to mental health")
            # report = await researcher.write_report()
            # return report'''
        #print("Background: ", json.loads(self.query).get('Background'))
        #query_as_dict = json.loads(self.query)
        #print("Background: ", {key: query_as_dict[key] for key in list(query_as_dict.keys())[1:]})
        #background = json.loads(self.query).get('Background')
        report = await researcher.write_report(self.query)

        return report
