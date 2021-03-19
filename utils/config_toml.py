# -*- coding: utf-8 -*-

"""
Defines :
 The ConfigToml class, derived from Config

"""


import toml

from utils.config import Config


class ConfigToml(Config):

    """
    Class derived from Config, specific to information being stored in a .toml file.

    Warning
    -------
    The class should not be instantiated directly, but rather through the Config.create
    factory method, that will return the appropriate derived class (depending on the
    type of file holding those parameters).

    """

    def load(self) -> None:
        """Loads values from the toml file."""
        toml_dict = toml.load(self.config_file)
        for name, value in toml_dict.items():
            self._load_parameter(name, value)

    def save(self) -> None:
        """
        Saves values to the toml file.

        The method keeps the eventual comments in the original file.
        """
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
                    toml_single_value_dict = {parameter_name: value}
                    new_line = toml.dumps(toml_single_value_dict)
                    parameters_saved.append(parameter_name)
                new_content += new_line
            for name, value in [
                item for item in self.data.items() if not item[0] in parameters_saved
            ]:
                new_line = f"{name} = {value}"
                new_content += new_line + "\n"
        with open(self.config_file, "w") as toml_file:
            toml_file.write(new_content)
