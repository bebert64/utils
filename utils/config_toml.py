# -*- coding: utf-8 -*-

"""
Defines :
 The ConfigToml class, derived from Config

"""


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

    def load_data(self) -> None:
        toml_dict = toml.load(self.config_file)
        for name, value in toml_dict.items():
            self._load_parameter(name, value)

    def save_data(self):
        pass
