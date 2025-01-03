from gpt_researcher.skills.researcher import ResearchConductor
from gpt_researcher.actions.utils import stream_output
from gpt_researcher.actions.query_processing import get_search_results

class MedResearchConductor(ResearchConductor):

    def __init__(
        self,
        researcher,
    ):
        super(MedResearchConductor, self).__init__(researcher)
        self.retriever_include_raw_content = True
        self.max_search_results_per_query = 1

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

    async def generate_global_context(self, query):
        await stream_output(
            "logs",
            "generate_global_context",
            f"🌐 Browsing the web to get context about the task: {query}...",
            self.researcher.websocket,
        )
        new_search_urls = []

        search_results = await get_search_results(query, self.researcher.retrievers[0])
        search_urls = [url.get("href") for url in search_results]
        new_search_urls.extend(search_urls)
        new_search_urls = await self.__get_new_urls(new_search_urls)


        self.researcher.context = search_results