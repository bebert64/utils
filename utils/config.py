# -*- coding: utf-8 -*-

"""
Defines :
 The Config class

"""


from __future__ import annotations

import pathlib
from typing import Dict, Optional, Union

ParameterValue = Union[int, str]
Parameters = Dict[str, ParameterValue]


class Config:

    def __init__(self, config_file: pathlib.Path):
        self.data = {}
        self.config_file = config_file

    @staticmethod
    def create(
        config_file: pathlib.Path, options: Optional[Parameters] = None
    ) -> Config:
        config = Config._create_config_object(config_file)
        assert hasattr(config, "load")
        config.load()
        config.load_options(options)
        return config

    @staticmethod
    def _create_config_object(config_file):
        if config_file.suffix == ".toml":
            from utils.config_toml import ConfigToml
            config = ConfigToml(config_file)
        elif config_file.suffix in [".ini", ".txt"]:
            from utils.config_database import ConfigDatabase
            config = ConfigDatabase(config_file)
        else:
            raise ValueError(
                f"{config_file} is of type {config_file.suffix}. The only acceptable "
                f"types are toml, ini, txt."
            )
        return config

    def __getitem__(self, item):
        return self.data[item]

    def __setitem__(self, item, value):
        self.data[item] = value

    def load_options(self, options: Optional[Parameters]) -> None:
        if options is not None:
            for item, value in options.items():
                self[item] = value

    def _load_parameter(self, name, value):
        if isinstance(value, str) and value.startswith("PathObject:"):
            path_as_string = value[len("PathObject:"):]
            value = pathlib.Path(path_as_string)
        self[name] = value
