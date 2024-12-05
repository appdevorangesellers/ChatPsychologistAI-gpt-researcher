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
from graphrag.cli.main import (
    path_autocomplete,
    SearchType,
)

app = typer.Typer(
    help="GraphRAG Extra: Extension of GraphRAG",
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

@app.command("extract")
def _extract_cli(
    method: Annotated[SearchType, typer.Option(help="The query algorithm to use.")],
    query: Annotated[str, typer.Option(help="The query to execute.")],
    config: Annotated[
        Path | None,
        typer.Option(
            help="The configuration to use.",
            exists=True,
            file_okay=True,
            readable=True,
            autocompletion=path_autocomplete(
                file_okay=True, dir_okay=False, match_wildcard="*"
            ),
        ),
    ] = None,
    data: Annotated[
        Path | None,
        typer.Option(
            help="Indexing pipeline output directory (i.e. contains the parquet files).",
            exists=True,
            dir_okay=True,
            readable=True,
            resolve_path=True,
            autocompletion=path_autocomplete(
                file_okay=False, dir_okay=True, match_wildcard="*"
            ),
        ),
    ] = None,
    root: Annotated[
        Path,
        typer.Option(
            help="The project root directory.",
            exists=True,
            dir_okay=True,
            writable=True,
            resolve_path=True,
            autocompletion=path_autocomplete(
                file_okay=False, dir_okay=True, match_wildcard="*"
            ),
        ),
    ] = Path(),  # set default to current directory
    community_level: Annotated[
        int,
        typer.Option(
            help="The community level in the Leiden community hierarchy from which to load community reports. Higher values represent reports from smaller communities."
        ),
    ] = 2,
    dynamic_community_selection: Annotated[
        bool,
        typer.Option(help="Use global search with dynamic community selection."),
    ] = False,
    response_type: Annotated[
        str,
        typer.Option(
            help="Free form text describing the response type and format, can be anything, e.g. Multiple Paragraphs, Single Paragraph, Single Sentence, List of 3-7 Points, Single Page, Multi-Page Report. Default: Multiple Paragraphs"
        ),
    ] = "Multiple Paragraphs",
    streaming: Annotated[
        bool, typer.Option(help="Print response in a streaming manner.")
    ] = False,
):
    """Query a knowledge graph index."""
    from graphrag_extra.cli.extract import run_global_extract
    #from graphrag_extra.cli.extract import run_global_search

    match method:
        case SearchType.GLOBAL:
            # run_global_search(
            run_global_extract(
                config_filepath=config,
                data_dir=data,
                root_dir=root,
                community_level=community_level,
                dynamic_community_selection=dynamic_community_selection,
                response_type=response_type,
                streaming=streaming,
                query=query,
            )
        case _:
            raise ValueError(INVALID_METHOD_ERROR)