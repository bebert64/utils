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

    def load(self) -> None:
        toml_dict = toml.load(self.config_file)
        for name, value in toml_dict.items():
            self._load_parameter(name, value)

    def save(self):
        new_content = ""
        parameters_saved = []
        with open(self.config_file, "r") as toml_file:
            for line in toml_file.readlines():
                parameter_name = line.split(" ")[0]
                try:
                    value = self[parameter_name]
                except KeyError:
                    new_line = line
                else:
                    value = self._translate_value(value)
                    new_line = f"{parameter_name} = '{value}'\n"
                    parameters_saved.append(parameter_name)
                new_content += new_line
            for name, value in [item for item in self.data.items() if not item[0] in parameters_saved]:
                new_line = f"{name} = {value}"
                new_content += new_line + "\n"
        with open(self.config_file, "w") as toml_file:
            toml_file.write(new_content)
