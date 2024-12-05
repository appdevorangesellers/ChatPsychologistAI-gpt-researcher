# Copyright (c) 2024 Microsoft Corporation.
# Licensed under the MIT License

"""CLI implementation of query subcommand."""

import asyncio
import sys
from pathlib import Path

import pandas as pd

import graphrag.api as api
from graphrag.config.load_config import load_config
from graphrag.config.models.graph_rag_config import GraphRagConfig
from graphrag.config.resolve_path import resolve_paths
from graphrag.index.create_pipeline_config import create_pipeline_config
from graphrag.logging.print_progress import PrintProgressReporter
from graphrag.utils.storage import _create_storage, _load_table_from_storage

from graphrag.cli.query import _resolve_parquet_files
from graphrag_extra.query.factories import (
    get_global_extract_engine,
)
from graphrag_extra import api
# from graphrag_extra.api.query import _reformat_context_data

reporter = PrintProgressReporter("")

from graphrag import cli


def run_global_extract(
    config_filepath: Path | None,
    data_dir: Path | None,
    root_dir: Path,
    community_level: int | None,
    dynamic_community_selection: bool,
    response_type: str,
    streaming: bool,
    query: str,
):
    '''def test():
        print("get_global_search_engine")
    from graphrag import api
    api.query.get_global_search_engine = get_global_extract_engine'''
    from graphrag import cli

    cli.query.api = api
    '''cli.query.api.global_search = api.query.global_extract
    response, context_data = asyncio.run(
        cli.query.run_global_search(
            config_filepath,
            data_dir,
            root_dir,
            community_level,
            dynamic_community_selection,
            response_type,
            streaming,
            query
        )
    )'''
    response, context_data = cli.query.run_global_search(
        config_filepath,
        data_dir,
        root_dir,
        community_level,
        dynamic_community_selection,
        response_type,
        streaming,
        query
    )

    reporter.success(f"--context_data--\n{context_data}")

    return context_data