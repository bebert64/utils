import pathlib
from typing import List, Any

import toml

from utils.config import Config


class ConfigToml(Config):
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

    def __init__(self, toml_path: pathlib.Path) -> None:
        self.toml_path: pathlib.Path = toml_path
        self._reserved_attribute_names: List[str] = []
        self.add_regular_attributes()

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
        self._set_reserved_attribute_names()
        self._add_attributes_from_toml_file()
        # self._add_attributes_from_options()

    def _add_attributes_from_toml_file(self) -> None:
        toml_dict = toml.load(self.toml_path)
        for attribute_name, attribute_value in toml_dict.items():
            self._add_attribute(attribute_name, attribute_value)