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
from .skills.data_researcher import DataResearchConductor
from .utils.enum import Tone
from .vector_store import VectorStoreWrapper
from langchain_chroma import Chroma
from pathlib import Path
from graphrag.cli.index import index_cli
from graphrag.logging.types import ReporterType
from graphrag.index.emit.types import TableEmitterType
from graphrag.logging.types import ReporterType
import asyncio
import subprocess

async def read_stream(stream, prefix):
    """Read and print lines from an async stream."""
    output = []
    async for line in stream:
        decoded_line = line.decode().strip()
        output.append(decoded_line)
        print(f"{prefix}: {decoded_line}")
    return '\n'.join(output)

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
        #self.vector_store = VectorStoreWrapper(Chroma(persist_directory="./scrape-embeddings",
        #                                              embedding_function=self.memory.get_embeddings()
        #                                              ))
        self.vector_store = None
        self.research_conductor: ResearchConductor = ResearchConductor(self)
        self.data_research_conductor: DataResearchConductor = DataResearchConductor(self)
        self.report_generator: ReportGenerator = ReportGenerator(self)
        self.context_manager: ContextManager = ContextManager(self)
        self.scraper_manager: BrowserManager = BrowserManager(self)

    async def conduct_data_research(self, query):
        print("conduct_data_research")
        # self.context = await self.research_conductor.conduct_research()
        await self.data_research_conductor.conduct_research(query)
        #subprocess.run(['graphrag', 'index', '--root', './ragtest'])

    async def conduct_research(self, query):
        print("conduct_research")
        #from .scraper.pymupdf.pymupdf import PyMuPDFScraper
        # self.context = await self.research_conductor.conduct_research()
        await self.research_conductor.conduct_research(query)
        # await index_cli(root=Path('./ragtest'))
        #PyMuPDFScraper('https://iris.who.int/bitstream/handle/10665/375767/9789240077263-eng.pdf?sequence=1&isAllowed=y').scrape()

        subprocess.run(['graphrag', 'index', '--root', './ragtest'])
        # output = subprocess.check_call(['graphrag_extra', 'init2'])
        # return self.context

    async def write_report(self, search_queries, mental_data) -> str:
        #from graphrag.query import factories
        #from graphrag_extra.query.structured_search.global_search.search import GlobalSearch
        #factories.GlobalSearch = GlobalSearch
        # context = await self.research_conductor.get_relevant_context(query)
        context = await self.data_research_conductor.extract_relevant_data(search_queries)
        print("context", context)
        return await self.report_generator.write_report(mental_data, context)
        #GlobalSearch().asearch_test()

        #subprocess.run(['graphrag_extra', 'extract', '--root', './ragtest', '--method', 'global', '--query', 'mental disorders'])
        #subprocess.run(['graphrag', 'query', '--root', './ragtest', '--method', 'global', '--query', 'mental disorders'])


        '''process = await asyncio.create_subprocess_exec(
            'graphrag_extra', 'extract', '--root', './ragtest', '--method', 'local', '--query', 'mental disorders',
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE
        )

        stdout_output, stderr_output = await asyncio.gather(
            read_stream(process.stdout, "stdout"),
            read_stream(process.stderr, "stderr")
        )

        rc = await process.wait()


        print('---------------------')
        print('stdout_output', stdout_output)
        print('---------------------')'''

    def get_research_sources(self) -> List[Dict[str, Any]]:
        return self.research_sources

    def get_data_research_sub_queries(self):
        return self.data_research_conductor.sub_queries

    def add_research_sources(self, sources: List[Dict[str, Any]]) -> None:
        self.research_sources.extend(sources)

    def get_costs(self) -> float:
        return self.research_costs

    def add_costs(self, cost: float) -> None:
        if not isinstance(cost, (float, int)):
            raise ValueError("Cost must be an integer or float")
        self.research_costs += cost
