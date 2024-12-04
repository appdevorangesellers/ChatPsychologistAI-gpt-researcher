# Copyright (c) 2024 Microsoft Corporation.
# Licensed under the MIT License

"""CLI entrypoint."""

import os
import re
from collections.abc import Callable
from enum import Enum
from pathlib import Path
from typing import Annotated

import typer

from graphrag.index.emit.types import TableEmitterType
from graphrag.logging.types import ReporterType
from graphrag.prompt_tune.defaults import (
    MAX_TOKEN_COUNT,
    MIN_CHUNK_SIZE,
    N_SUBSET_MAX,
    K,
)
from graphrag.prompt_tune.types import DocSelectionType

INVALID_METHOD_ERROR = "Invalid method"

app = typer.Typer(
    help="GraphRAG: A graph-based retrieval-augmented generation (RAG) system.",
    no_args_is_help=True,
)

@app.command("init")
def _initialize_cli(

):
    print("GraphRAG extra")


@app.command("init2")
def _initialize_cli2(

):
    # print("GraphRAG extra 2")
    return "GraphRAG extra 2"
