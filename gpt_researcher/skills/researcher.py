import asyncio
import json
import random

from ..actions.query_processing import plan_research_outline, get_search_results
from ..actions.utils import stream_output
from ..document import DocumentLoader
from ..actions import (
    generate_files,
)

class ResearchConductor:
    """Manages and coordinates the research process."""

    def __init__(self, researcher):
        self.researcher = researcher

    async def get_relevant_context(self, query):
        query_as_dict = json.loads(query)

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
            )

        # return context


    async def conduct_research(self, query):
        """
        Runs the GPT Researcher to conduct research
        """
        # Reset visited_urls and source_urls at the start of each research task
        '''self.researcher.visited_urls.clear()
        if self.researcher.verbose:
            await stream_output(
                "logs",
                "starting_research",
                f"🔎 Starting the research task for '{query}'...",
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

        # await self.__get_context_by_search(query, document_data)'''

        context = await self.__get_context_by_search(query)

        # self.researcher.context = f"Context from local documents:
        # {docs_context}\n\nContext from web sources: {web_context}"

        if self.researcher.verbose:
            await stream_output(
                "logs",
                "research_step_finalized",
                f"Finalized research step.\n💸 Total Research Costs: ${self.researcher.get_costs()}",
                self.researcher.websocket,
            )

        # return self.researcher.context
        return context


    async def __get_context_by_vectorstore(self, query):
        """
        Generates the context for the research task by searching the vectorstore
        Returns:
            context: List of context
        """
        context = []
        # Generate Sub-Queries including original query
        # sub_queries = await self.plan_research(query)
        # sub_queries.append(query)
        sub_queries = [query]

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


    async def __get_context_by_search(self, query, scraped_data: list = []):
        """
        Generates the context for the research task by searching the query and scraping the results
        Returns:
            context: List of context
        """
        context = []
        # Generate Sub-Queries including original query
        sub_queries = await self.plan_research(query)
        # sub_queries.append(query)

        if self.researcher.verbose:
            await stream_output(
                "logs",
                "subqueries",
                f"🗂️ I will conduct my research based on the following queries: {sub_queries}...",
                self.researcher.websocket,
                True,
                sub_queries,
            )

        # Using asyncio.gather to process the sub_queries asynchronously
        context = await asyncio.gather(
        # await asyncio.gather(
            *[
                self.__process_sub_query(sub_query, scraped_data)
                for sub_query in sub_queries
            ]
        )
        # return context


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


    async def __process_sub_query(self, sub_query: str, scraped_data: list = []):
        """Takes in a sub query and scrapes urls based on it and gathers context.

        Args:
            sub_query (str): The sub-query generated from the original query
            scraped_data (list): Scraped data passed in

        Returns:
            str: The context gathered from search
        """
        if self.researcher.verbose:
            await stream_output(
                "logs",
                "running_subquery_research",
                f"\n🔍 Running research for '{sub_query}'...",
                self.researcher.websocket,
            )

        if not scraped_data:
            # scraped_data = await self.__scrape_data_by_query(sub_query)
            await self.__scrape_data_by_query(sub_query)

        content = await self.researcher.context_manager.get_similar_content_by_query(sub_query, scraped_data)

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
        # return content
        # return scraped_data


    async def __get_new_urls(self, url_set_input):
        """Gets the new urls from the given url set.
        Args: url_set_input (set[str]): The url set to get the new urls from
        Returns: list[str]: The new urls from the given url set
        """

        new_urls = []
        for url in url_set_input:
            if url not in self.researcher.visited_urls:
                self.researcher.visited_urls.add(url)
                new_urls.append(url)
                if self.researcher.verbose:
                    await stream_output(
                        "logs",
                        "added_source_url",
                        f"✅ Added source url to research: {url}\n",
                        self.researcher.websocket,
                        True,
                        url,
                    )

        return new_urls


    async def __scrape_data_by_query(self, sub_query):
        """
        Runs a sub-query across multiple retrievers and scrapes the resulting URLs.

        Args:
            sub_query (str): The sub-query to search for.

        Returns:
            list: A list of scraped content results.
        """
        new_search_urls = []

        # Iterate through all retrievers
        for retriever_class in self.researcher.retrievers:
            # Instantiate the retriever with the sub-query
            retriever = retriever_class(sub_query)

            # Perform the search using the current retriever
            search_results = await asyncio.to_thread(
                retriever.search, max_results=self.researcher.cfg.max_search_results_per_query
            )

            # Collect new URLs from search results
            search_urls = [url.get("href") for url in search_results]
            new_search_urls.extend(search_urls)

        # Get unique URLs
        new_search_urls = await self.__get_new_urls(new_search_urls)
        random.shuffle(new_search_urls)

        # Log the research process if verbose mode is on
        if self.researcher.verbose:
            await stream_output(
                "logs",
                "researching",
                f"🤔 Researching for relevant information across multiple sources b ...\n",
                self.researcher.websocket,
            )

        # Scrape the new URLs
        scraped_content = await self.researcher.scraper_manager.browse_urls(new_search_urls)

        if self.researcher.vector_store:
            self.researcher.vector_store.load(scraped_content)

        await asyncio.gather(
            *[
                generate_files(item["raw_content"], item["url"])
                for item in scraped_content
            ]
        )

        if self.researcher.verbose:
            await stream_output(
                "logs",
                "researching_web_vector_db",
                f"🤔 Information across multiple sources added as embedded vectors ...\n",
                self.researcher.websocket,
            )

        #return scraped_content

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
