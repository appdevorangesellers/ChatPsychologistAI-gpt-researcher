import re
from abc import ABCMeta, abstractmethod
from collections.abc import Iterator
from typing import Any

from graphrag.logging.base import ProgressReporter


class PipelineStorage(metaclass=ABCMeta):
    """Provide a storage interface for the pipeline. This is where the pipeline will store its output data."""

    @abstractmethod
    async def get(
        self, key: str, as_bytes: bool | None = None, encoding: str | None = None
    ) -> Any:
        """Get the value for the given key.

        Args:
            - key - The key to get the value for.
            - as_bytes - Whether or not to return the value as bytes.

        Returns
        -------
            - output - The value for the given key.
        """

    @abstractmethod
    async def set(self, key: str, value: Any, encoding: str | None = None) -> None:
        """Set the value for the given key.

        Args:
            - key - The key to set the value for.
            - value - The value to set.
        """