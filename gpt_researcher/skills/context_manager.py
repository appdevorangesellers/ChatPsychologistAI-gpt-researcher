import asyncio
from typing import List, Dict, Optional, Set

from ..context.compression import VectorstoreCompressor, ContextCompressor
from ..actions.utils import stream_output


class ContextManager:
    """Manages context for the researcher agent."""

    def __init__(self, researcher):
        self.researcher = researcher

    async def get_similar_content_by_query(self, query, pages):
        if self.researcher.verbose:
            await stream_output(
                "logs",
                "fetching_query_content",
                f"📚 Getting relevant content based on query: {query}...",
                self.researcher.websocket,
            )

        context_compressor = ContextCompressor(
            documents=pages, embeddings=self.researcher.memory.get_embeddings()
        )
        return await context_compressor.async_get_context(
            query=query, max_results=10, cost_callback=self.researcher.add_costs
        )

    async def get_similar_content_by_query_with_vectorstore(self, query):
        if self.researcher.verbose:
            await stream_output(
                "logs",
                "fetching_query_format",
                f" Getting relevant content based on query: {query}...",
                self.researcher.websocket,
                )
        # vectorstore_compressor = VectorstoreCompressor(self.researcher.vector_store, filter)
        vectorstore_compressor = VectorstoreCompressor(
            vector_store=self.researcher.vector_store
        )
        return await vectorstore_compressor.async_get_context(
           query=query, max_results=10, cost_callback=self.researcher.add_costs
       )
