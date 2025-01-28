import asyncio
from ...actions.query_processing import generate_subtopic_key_discrepancy
from gpt_researcher.actions.utils import stream_output

async def read_stream(stream, prefix):
    """Read and print lines from an async stream."""
    output = []
    async for line in stream:
        decoded_line = line.decode().strip()
        output.append(decoded_line)
        print(f"{prefix}: {decoded_line}")
    return '\n'.join(output)

class TopicResearchConductor:
    def __init__(
        self,
        researcher,
    ):
        self.researcher = researcher

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

    async def conduct_diagnoses_research(self, topic, topic_data):
        """
        Runs the GPT Researcher to conduct research
        """
        sub_queries = await self.plan_research(topic, topic_data)
        # sub_queries.append(query)
        print('sub_queries', sub_queries)
        #self.sub_queries = sub_queries
        print(f"possible disorders for {sub_queries.strip()} in {topic}")
        return await self.extract_relevant_data(f"possible disorders for {sub_queries.strip()} in {topic}")

    async def plan_research(self, topic, topic_data):
        await stream_output(
            "logs",
            "planning_research",
            f"🤔 Planning the research strategy and subtasks (this may take a minute)...",
            self.researcher.websocket,
        )

        return await generate_subtopic_key_discrepancy(
            query=topic,
            context=topic_data,
            cfg=self.researcher.cfg,
            cost_callback=self.researcher.add_costs,
        )