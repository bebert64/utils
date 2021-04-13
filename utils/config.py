# -*- coding: utf-8 -*-

"""
Defines :
 The Config class

"""


from __future__ import annotations

import pathlib
from typing import Dict, Optional, Union, Any

ParameterValue = Union[int, str, pathlib.Path]
Parameters = Dict[str, ParameterValue]


class Config:

    """
    The Config class holds parameters' values that can be shared between all modules.

    The types that can be stored and retrieved are str, int, pathlib.Path and array
    of a single type.
    Values are accessed with the bracket notation (config[parameter_name]).

    Warning
    -------
    The class should not be instantiated directly, but rather through the Config.create
    factory method, that will return the appropriate derived class (depending on the
    type of file holding those parameters).

    """

    def __init__(self, config_file: pathlib.Path) -> None:
        self.data: Parameters = {}
        self.config_file = config_file

    @staticmethod
    def create(
        config_file: pathlib.Path, options: Optional[Parameters] = None
    ) -> Config:
        """
        Factory method to create a config object.

        Depending on the extension of the file given as input, the appropriate
        derived class will be called. Two options are available : either the values can
        be stored in a toml file, or they are stored in a sqlite database. In that
        second case, all values should be in a table named "Parameter", with columns
        "name", "value", "description" and "group".

        Parameters
        ----------
        config_file:
            The file holding the main information. That file can either be a toml file,
            directly holding the parameter values, or a .txt or .ini file, with a
            single line holding the path to a sqlite database.
        options:
            A dictionary can be given at creation, with values meant to override
            existing default values, or with entirely new parameters not present in the
            default parameters.

        """
        # create_main_widget is a factory method, and should therefore be allowed
        # to access protected members of the class.
        # pylint: disable = protected-access
        config = Config._create_config_object(config_file)
        assert hasattr(config, "load")
        config.load()  # type: ignore
        config._load_options(options)
        return config

    @staticmethod
    def _create_config_object(config_file: pathlib.Path) -> Config:
        # We only import the appropriate subclass, because they each have specific
        # dependencies.
        # pylint: disable = import-outside-toplevel
        if config_file.suffix == ".toml":
            from utils.config_toml import ConfigToml

            config: Config = ConfigToml(config_file)
        elif config_file.suffix in [".ini", ".txt"]:
            from utils.config_database import ConfigDatabase

            config = ConfigDatabase(config_file)
        else:
            raise ValueError(
                f"{config_file} is of type {config_file.suffix}. The only acceptable "
                f"types are toml, ini, txt."
            )
        return config

    def __getitem__(self, item: str) -> Any:
        return self.data[item]

    def __setitem__(self, item: str, value: Any) -> None:
        self.data[item] = value

    def _load_options(self, options: Optional[Parameters]) -> None:
        if options is not None:
            for item, value in options.items():
                self[item] = value

    def _load_parameter(self, name: str, value: Any) -> None:
        if isinstance(value, str) and value.startswith("PathObject:"):
            path_as_string = value[len("PathObject:") :]
            value = pathlib.Path(path_as_string)
        self[name] = value

    @staticmethod
    def translate_value(value: ParameterValue) -> ParameterValue:
        """
        Transforms a pathlib.Path object in a string.

        The way the string is formed, with a specific prefix, allows to keep the
        information that this value is meant to represent a path. This way, the
        parameter can directly be retrieved as a Path object when the value is read
        from wherever it is stored.

        """
        if isinstance(value, pathlib.Path):
            value = "PathObject:" + str(value)
        return value
