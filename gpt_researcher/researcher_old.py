import asyncio

from ..actions.query_processing import plan_research_outline, get_search_results
from ..actions.utils import stream_output
from ..document import DocumentLoader

class ResearchConductor:
    """Manages and coordinates the research process."""

    def __init__(self, researcher):
        self.researcher = researcher

    async def conduct_research(self):
        """
        Runs the GPT Researcher to conduct research
        """

        if self.researcher.verbose:
            await stream_output(
                "logs",
                "starting_research",
                f"🔎 Starting the research task for '{self.researcher.query}'...",
                self.researcher.websocket,
            )
            await stream_output(
                "logs",
                "agent_generated",
                self.researcher.agent,
                self.researcher.websocket
            )

        # Hybrid search including both local documents and web sources
        document_data = await DocumentLoader(self.researcher.cfg.doc_path).load()
        if len(document_data) > 0 and self.researcher.vector_store:
            self.researcher.vector_store.load(document_data)
		
		docs_context = await self.__get_context_by_search(self.researcher.query, document_data)
        web_context = await self.__get_context_by_search(self.researcher.query)
        self.researcher.context = f"Context from local documents: {docs_context}\n\nContext from web sources: {web_context}"
        # self.researcher.context = await self.__get_context_by_search(self.researcher.query, document_data)
        # self.researcher.context = await self.__get_context_by_vectorstore(self.researcher.query)

        if self.researcher.verbose:
            await stream_output(
                "logs",
                "research_step_finalized",
                f"Finalized research step.\n💸 Total Research Costs: ${self.researcher.get_costs()}",
                self.researcher.websocket,
            )

        return self.researcher.context

    async def __get_context_by_vectorstore(self, query):
        """
        Generates the context for the research task by searching the vectorstore
        Returns:
            context: List of context
        """
        context = []
        # Generate Sub-Queries including original query
        sub_queries = await self.plan_research(query)
        sub_queries.append(query)

        if self.researcher.verbose:
            await stream_output(
                "logs",
                "subqueries",
                f"🗂️  I will conduct my research based on the following queries: {sub_queries}...",
                self.researcher.websocket,
                True,
                sub_queries,
            )

        # Using asyncio.gather to process the sub_queries asynchronously
        context = await asyncio.gather(
            *[
                self.__process_sub_query_with_vectorstore(sub_query)
                for sub_query in sub_queries
            ]
        )
        return context

    async def __process_sub_query_with_vectorstore(self, sub_query: str):
        """Takes in a sub query and gathers context from the user provided vector store

        Args:
           sub_query (str): The sub-query generated from the original query

        Returns:
           str: The context gathered from search
        """
        if self.researcher.verbose:
            await stream_output(
                "logs",
                "running_subquery_with_vectorstore_research",
                f"\n🔍 Running research for '{sub_query}'...",
                self.researcher.websocket,
            )

        content = await self.researcher.context_manager.get_similar_content_by_query_with_vectorstore(sub_query)

        if content and self.researcher.verbose:
            await stream_output(
                "logs", "subquery_context_window", f"📃 {content}", self.researcher.websocket
            )
        elif self.researcher.verbose:
            await stream_output(
                "logs",
                "subquery_context_not_found",
                f"🤷 No content found for '{sub_query}'...",
                self.researcher.websocket,
            )
        return content

    async def plan_research(self, query):
        await stream_output(
            "logs",
            "planning_research",
            f"🌐 Browsing the web to learn more about the task: {query}...",
            self.researcher.websocket,
        )

        search_results = await get_search_results(query, self.researcher.retrievers[0])

        await stream_output(
            "logs",
            "planning_research",
            f"🤔 Planning the research strategy and subtasks (this may take a minute)...",
            self.researcher.websocket,
        )

        return await plan_research_outline(
            query=query,
            search_results=search_results,
            cfg=self.researcher.cfg,
            cost_callback=self.researcher.add_costs,
        )
