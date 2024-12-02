from typing import Dict, Optional
import json

from ..actions import (
    stream_output,
    generate_report,
)


class ReportGenerator:
    """Generates reports based on research data."""

    def __init__(self, researcher):
        self.researcher = researcher
        self.research_params = {
            # "query": self.researcher.query,
            "agent_role_prompt": self.researcher.cfg.agent_role or self.researcher.role,
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

        report = await generate_report(**report_params)

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