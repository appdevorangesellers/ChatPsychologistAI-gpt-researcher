import logging
import os
import re
import shutil
from collections.abc import Iterator
from pathlib import Path
from typing import Any, cast

import aiofiles
from aiofiles.os import remove
from aiofiles.ospath import exists
from datashaper import Progress

from .pipeline_storage import PipelineStorage
from graphrag.logging.base import ProgressReporter
from ..utils.storage_context import PipelineQueryStats, PipelineQueryWrapper
import json
from dataclasses import asdict

log = logging.getLogger(__name__)


class FilePipelineStorage(PipelineStorage):
    """File storage class definition."""

    _root_dir: str
    _encoding: str

    def __init__(self, root_dir: str | None = None, encoding: str | None = None):
        """Init method definition."""
        self._root_dir = root_dir or ""
        self._encoding = encoding or "utf-8"
        Path(self._root_dir).mkdir(parents=True, exist_ok=True)

    async def _read_file(
        self,
        path: str | Path,
        as_bytes: bool | None = False,
        encoding: str | None = None,
    ) -> Any:
        """Read the contents of a file."""
        read_type = "rb" if as_bytes else "r"
        encoding = None if as_bytes else (encoding or self._encoding)

        async with aiofiles.open(
            path,
            cast(Any, read_type),
            encoding=encoding,
        ) as f:
            return await f.read()

    async def get(
        self, key: str, as_bytes: bool | None = False, encoding: str | None = None
    ) -> Any:
        """Get method definition."""
        file_path = join_path(self._root_dir, key)

        if await self.has(key):
            return await self._read_file(file_path, as_bytes, encoding)
        if await exists(key):
            # Lookup for key, as it is pressumably a new file loaded from inputs
            # and not yet written to storage
            return await self._read_file(key, as_bytes, encoding)

        return None

    async def set(self, key: str, value: Any, encoding: str | None = None) -> None:
        """Set method definition."""
        is_bytes = isinstance(value, bytes)
        write_type = "wb" if is_bytes else "w"
        encoding = None if is_bytes else encoding or self._encoding

        old_content = await self.get(key, is_bytes, encoding)
        content = PipelineQueryWrapper()
        #content = {"queries": []}
        print("old_content", old_content)

        if old_content:
            old_content = json.loads(old_content)
            content.queries = old_content['queries']
            #content.queries.append(old_content)

        content.queries.append(value)

        content = json.dumps(asdict(content), indent=4, ensure_ascii=False)

        async with aiofiles.open(
            join_path(self._root_dir, key),
            cast(Any, write_type),
            encoding=encoding,
        ) as f:
            # await f.write(value)
            await f.write(content)

    async def has(self, key: str) -> bool:
        """Has method definition."""
        return await exists(join_path(self._root_dir, key))

def join_path(file_path: str, file_name: str) -> Path:
    """Join a path and a file. Independent of the OS."""
    return Path(file_path) / Path(file_name).parent / Path(file_name).name


def create_file_storage(out_dir: str | None) -> PipelineStorage:
    """Create a file based storage."""
    log.info("Creating file storage at %s", out_dir)
    return FilePipelineStorage(out_dir)
