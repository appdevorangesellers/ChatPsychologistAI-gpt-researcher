from typing import Set, List, Dict, Any

from .actions import (
    get_retrievers
)
from .config import Config
from .llm_provider import GenericLLMProvider
from .memory import Memory
from .skills.browser import BrowserManager
from .skills.context_manager import ContextManager
from .skills.writer import ReportGenerator
from .skills.researcher import ResearchConductor
from .utils.enum import Tone
from .vector_store import VectorStoreWrapper
from langchain_chroma import Chroma


class GPTResearcher:
    def __init__(
            self,
            # query: str,
            tone: Tone = Tone.Objective,
            config_path="default",
            websocket=None,
            verbose: bool = True
    ):
        # self.query = query
        self.cfg = Config(config_path)
        self.llm = GenericLLMProvider(self.cfg)
        self.tone = tone if isinstance(tone, Tone) else Tone.Objective
        self.source_urls = []
        self.research_sources = []
        self.websocket = websocket
        self.agent = "🧠 Psychological Assessment Agent"
        self.role = "You are an experienced psychological assessment assistant. Your main task is to offer a comprehensive, insightful, and unbiased analysis of the provided information, offering general guidance based on psychological theories and frameworks. However, be aware that a full diagnosis requires professional evaluation by a licensed mental health expert."
        self.visited_urls = set()
        self.verbose = verbose
        self.context = []
        self.research_costs = 0.0
        self.retrievers = get_retrievers(self.cfg)
        self.memory = Memory(
            self.cfg.embedding_provider, self.cfg.embedding_model, **self.cfg.embedding_kwargs
        )
        self.vector_store = VectorStoreWrapper(Chroma(persist_directory="./scrape-embeddings",
                                                      embedding_function=self.memory.get_embeddings()
                                                      ))
        self.research_conductor: ResearchConductor = ResearchConductor(self)
        self.report_generator: ReportGenerator = ReportGenerator(self)
        self.context_manager: ContextManager = ContextManager(self)
        self.scraper_manager: BrowserManager = BrowserManager(self)

    async def conduct_research(self, query):
        print("conduct_research")
        # self.context = await self.research_conductor.conduct_research()
        await self.research_conductor.conduct_research(query)
        # return self.context

    async def write_report(self, query) -> str:
        context = await self.research_conductor.get_relevant_context(query)
        return await self.report_generator.write_report(query, context)

    def get_research_sources(self) -> List[Dict[str, Any]]:
        return self.research_sources

    def add_research_sources(self, sources: List[Dict[str, Any]]) -> None:
        self.research_sources.extend(sources)

    def get_costs(self) -> float:
        return self.research_costs

    def add_costs(self, cost: float) -> None:
        if not isinstance(cost, (float, int)):
            raise ValueError("Cost must be an integer or float")
        self.research_costs += cost
