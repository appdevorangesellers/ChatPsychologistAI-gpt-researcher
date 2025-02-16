from typing import Dict, Optional
import json
from ..utils.llm import construct_subtopics

from ..actions import (
    stream_output,
    generate_report,
    write_report_introduction
)

from gpt_researcher import actions

class ReportGenerator:
    """Generates reports based on research data."""

    def __init__(self, researcher):
        self.researcher = researcher
        self.research_params = {
            # "query": self.researcher.query,
            "agent_role_prompt": self.researcher.cfg.agent_role or self.researcher.role,
            "report_type": self.researcher.report_type,
            "tone": self.researcher.tone,
            "websocket": self.researcher.websocket,
            "cfg": self.researcher.cfg,
        }

    async def write_report(self, query, ext_context=None) -> str:
        """
        Write a report based on existing headers and relevant contents.

        Args:
            existing_headers (list): List of existing headers.
            relevant_written_contents (list): List of relevant written contents.
            ext_context (Optional): External context, if any.

        Returns:
            str: The generated report.
        """

        # context = ext_context or self.researcher.context
        context = ext_context
        if self.researcher.verbose:
            await stream_output(
                "logs",
                "writing_report",
                #f"✍️ Writing report for '{self.researcher.query}'...",
                f"✍️ Writing report ...",
                self.researcher.websocket,
            )

        report_params = self.research_params.copy()
        report_params["query"] = query
        report_params["context"] = context

        report_params["cost_callback"] = self.researcher.add_costs

        report = await actions.generate_report(**report_params)

        if self.researcher.verbose:
            await stream_output(
                "logs",
                "report_written",
                f"📝 Report written for '{query}'",
                self.researcher.websocket,
            )

            await stream_output(
                "logs",
                "writing_step_finalized",
                f"Finalized writing step.\n💸 Total Costs: ${self.researcher.get_costs()}",
                self.researcher.websocket,
            )

        return report

    async def get_subtopics(self, query):
        """Retrieve subtopics for the research."""
        if self.researcher.verbose:
            await stream_output(
                "logs",
                "generating_subtopics",
                f"🌳 Generating subtopics for '{query}'...",
                self.researcher.websocket,
            )

        subtopics = await construct_subtopics(
            task=query,
            data=self.researcher.context,
            config=self.researcher.cfg,
            subtopics=self.researcher.subtopics,
        )

        if self.researcher.verbose:
            await stream_output(
                "logs",
                "subtopics_generated",
                f"📊 Subtopics generated for '{query}'",
                self.researcher.websocket,
            )

        return subtopics

    async def write_introduction(self, query):
        """Write the introduction section of the report."""
        if self.researcher.verbose:
            await stream_output(
                "logs",
                "writing_introduction",
                f"✍️ Writing introduction for '{query}'...",
                self.researcher.websocket,
            )

        introduction = await write_report_introduction(
            query=query,
            context=self.researcher.context,
            agent_role_prompt=self.researcher.cfg.agent_role or self.researcher.role,
            config=self.researcher.cfg,
            websocket=self.researcher.websocket,
            cost_callback=self.researcher.add_costs,
        )

        if self.researcher.verbose:
            await stream_output(
                "logs",
                "introduction_written",
                f"📝 Introduction written for '{query}'",
                self.researcher.websocket,
            )

        return introduction
