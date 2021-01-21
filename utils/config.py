# -*- coding: utf-8 -*-

"""
Defines :
 The Config class

"""

import pathlib
from copy import copy
from typing import Any, Dict, Optional, Union, List

import toml

Option = Union[int, str]
Options = Dict[str, Option]


class MetaConfig(type):
    """
    The meta class is used to make sure these regular
    attributes are defined AFTER any specific implementations a derived class might
    want to do, so that in takes the "new" reserved names into account.
    """

    def __call__(cls, *args, **kwargs):
        config_object = type.__call__(cls, *args, **kwargs)
        config_object.add_regular_attributes()
        return config_object


class Config(metaclass=MetaConfig):
    """
    The Config object holds information we need to share among the various objects.

    All values from the config.toml file are added as attributes when
    add_regular_attributes is called. The meta class is used to make sure these regular
    attributes are defined AFTER any specific implementations a derived class might
    want to do, so that in takes the "new" reserved names into account.

    Parameters
    ----------
    toml_path
        The path to the toml file.
    options
        A dictionary containing additional configuration parameters. If a given
        parameter has the same name as one from the config.toml file, the new value
        will superseed the existing one.

    Error
    -----
    AttributeError
        A few names are reserved, and an error will be raised if they are found in
        the options dictionary.

    """

    def __init__(
        self, toml_path: pathlib.Path, options: Optional[Options] = None
    ) -> None:
        self.toml_path = toml_path
        self.options: Optional[Options] = options
        self._reserved_attribute_names: List[str] = []

    # By default, mypy complains that the attributes created dynamically by
    # the _add_attributes_from_toml_file method do not exist.
    # redefining __getattr__ with types makes mypy stop complaining.
    def __getattr__(self, name: str) -> Any:
        try:
            getattr(super(), name)
        except AttributeError as error:
            raise AttributeError(
                f"Parameter {name} has not been found in the config.toml file."
            ) from error

    def add_regular_attributes(self) -> None:
        """
        Adds attributes from the toml file and from the options.

        If there is need to reserve attribute names (in a derived class for example),
        this function should be called after such attributes are defined.

        """
        self._get_reserved_attribute_names()
        self._add_attributes_from_toml_file()
        self._add_attributes_from_options()

    def _get_reserved_attribute_names(self) -> List[str]:
        # To include all reserved names, must be run JUST BEFORE _add_attributes
        return copy(list(self.__dict__.keys()))

    def _add_attributes_from_toml_file(self) -> None:
        toml_dict = toml.load(self.toml_path)
        for attribute_name, attribute_value in toml_dict.items():
            self._add_attribute(attribute_name, attribute_value)

    def _add_attributes_from_options(self) -> None:
        if self.options is not None:
            for attribute_name, attribute_value in self.options.items():
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
