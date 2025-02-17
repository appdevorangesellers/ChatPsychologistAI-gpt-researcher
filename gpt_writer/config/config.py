import json
import os
import warnings

import gpt_researcher.config.variables.default
from .variables.default import DEFAULT_CONFIG
from gpt_researcher.config import Config as GptResearcherConfig
from typing import Dict, Any, List, Union, Type, get_origin, get_args
from gpt_researcher import config
from .variables import default
# config.Config.DEFAULT_CONFIG = DEFAULT_CONFIG
#GptResearcherConfig.variables.default = default
class Config(GptResearcherConfig):
    """Config class for GPT Researcher."""

    CONFIG_DIR = os.path.join(os.path.dirname(__file__), "variables")
    DEFAULT_CONFIG = DEFAULT_CONFIG

    def __init__(self, config_path: str | None = None):
        #config.Config.DEFAULT_CONFIG = DEFAULT_CONFIG
        super().__init__(config_path)

    def load_config_a(cls, config_path: str | None) -> Dict[str, Any]:
        print("load_config DEFAULT_CONFIG", DEFAULT_CONFIG)
        return super().load_config(config_path)
