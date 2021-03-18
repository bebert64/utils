# -*- coding: utf-8 -*-

"""
Defines :
 The Config class

"""


from __future__ import annotations

import pathlib
from copy import copy
from typing import Any, Dict, Optional, Union


ParameterValue = Union[int, str]
Parameters = Dict[str, ParameterValue]


class Config:

    @staticmethod
    def create(
        config_file: pathlib.Path, options: Optional[Parameters] = None
    ) -> Config:
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
        config.add_options(options)
        return config

    def _set_reserved_attribute_names(self):
        # To include all reserved names, must be run JUST BEFORE _add_attributes
        self._reserved_attribute_names = copy(list(self.__dict__.keys()))

    def add_options(self, options: Optional[Parameters]) -> None:
        if options is not None:
            for attribute_name, attribute_value in options.items():
                self._add_attribute(attribute_name, attribute_value)

    def _add_attribute(self, attribute_name: str, attribute_value: Any) -> None:
        is_attribute_reserved = self._is_attribute_reserved(attribute_name)
        if is_attribute_reserved:
            self._raise_attribute_exists_error(attribute_name)
        setattr(self, attribute_name, attribute_value)

    def _is_attribute_reserved(self, attribute_name: str) -> bool:
        return attribute_name in self._reserved_attribute_names

    def _raise_attribute_exists_error(self, attribute_name: str) -> None:
        error_message = f"""
The attribute name "{attribute_name}" is reserved by the config file, and cannot be
given to any attribute from the config.toml file. Please rename it before restarting
the application."""
        error_message_formatted = self._format_error_message(error_message)
        raise AttributeError(error_message_formatted)

    @staticmethod
    def _format_error_message(error_message: str) -> str:
        return error_message.replace("\n", " ").strip()
