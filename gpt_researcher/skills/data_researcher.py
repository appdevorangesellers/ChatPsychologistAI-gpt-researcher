import asyncio
import json
import random

from ..actions.query_processing import plan_research_outline, get_search_results
from ..actions.utils import stream_output
from ..document import DocumentLoader
from ..actions import (
    generate_files,
)

from .researcher import ResearchConductor
from graphrag.cli.query import run_global_search
from pathlib import Path
import subprocess
from typing import List

async def read_stream(stream, prefix):
    """Read and print lines from an async stream."""
    output = []
    async for line in stream:
        decoded_line = line.decode().strip()
        output.append(decoded_line)
        print(f"{prefix}: {decoded_line}")
    return '\n'.join(output)

class DataResearchConductor(ResearchConductor):
    async def extract_relevant_data(self, query: str):
        """Extract data for a query command."""
        print(f"Received extract request for /query - query: {query}")

        try:
            process = await asyncio.create_subprocess_exec(
                'graphrag_extra', 'extract', '--root', './rag', '--method', 'local', '--query', query,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE
            )
            print('here')
            stdout_output, stderr_output = await asyncio.gather(
                read_stream(process.stdout, "stdout"),
                read_stream(process.stderr, "stderr")
            )



            rc = await process.wait()
            print(rc)

            return stdout_output.split("--local_extract_response--")[1]
        except Exception as e:
            return e

    async def get_relevant_context(self, query):
        '''query_as_dict = json.loads(query)

        #background = query_as_dict.get('Background')
        background_web_context = await self.__get_context_by_search(query)

        # list(json.loads(self.query).keys())[1:]
        document_data = await DocumentLoader(self.researcher.cfg.doc_path).load()
        if len(document_data) > 0 and self.researcher.vector_store:
            self.researcher.vector_store.load(document_data)

        other_topics = {key: query_as_dict[key] for key in list(query_as_dict.keys())[1:]}
        vectorstore_context = await self.__get_context_by_vectorstore(f"Conduct a comprehensive psychological analysis and research based on the subject's: {background} together with {other_topics}")
        context = f"Background context from web sources: {background_web_context}\n\nContext from saved vector db: {vectorstore_context}"

        if self.researcher.verbose:
            await stream_output(
                "logs",
                "research_step_finalized",
                f"Finalized research step.\n💸 Total Research Costs: ${self.researcher.get_costs()}",
                self.researcher.websocket,
            )'''
        self.extract_context(query)

        # return context

    async def conduct_research(self, query):
        """
        Runs the GPT Researcher to conduct research
        """
        sub_queries = await self.plan_research(query)
        # sub_queries.append(query)
        print('sub_queries', sub_queries)
        self.sub_queries = sub_queries

    async def plan_research(self, query):
        await stream_output(
            "logs",
            "planning_research",
            f"🤔 Planning the research strategy and subtasks (this may take a minute)...",
            self.researcher.websocket,
        )

        return await plan_research_outline(
            query='',
            type="data",
            search_results=query,
            cfg=self.researcher.cfg,
            cost_callback=self.researcher.add_costs,
        )
