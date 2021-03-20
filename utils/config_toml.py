# -*- coding: utf-8 -*-

"""
Defines :
 The ConfigToml class, derived from Config

"""
from typing import List

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
        toml_writer = _TomlWriter(self)
        toml_writer.save()


class _TomlWriter:
    def __init__(self, config_toml: ConfigToml) -> None:
        self.config_toml: ConfigToml = config_toml
        self.new_content: str = ""
        self.parameters_saved: List[str] = []
        self.data = self.config_toml.data

    def save(self) -> None:
        # public method from private class, not documented
        # pylint: disable=missing-function-docstring
        self._reset()
        self._read()
        self._write()

    def _read(self) -> None:
        self._transform_existing_lines()
        self._add_new_lines()

    def _transform_existing_lines(self):
        with open(self.config_toml.config_file, "r") as toml_file:
            for line in toml_file.readlines():
                new_line = self._transform_line(line)
                self.new_content += new_line

    def _transform_line(self, line):
        key = line.split(" ")[0]
        try:
            value = self.data[key]
        except KeyError:
            new_line = line
        else:
            new_line = self._translate_value_toml(key, value)
            self.parameters_saved.append(key)
        return new_line

    def _add_new_lines(self):
        for key in [
            key for key in self.data.keys() if key not in self.parameters_saved
        ]:
            value = self.data[key]
            new_line = self._translate_value_toml(key, value)
            self.new_content += new_line

    def _translate_value_toml(self, key, value):
        value = self.config_toml.translate_value(value)
        toml_single_value_dict = {key: value}
        new_line = toml.dumps(toml_single_value_dict)
        return new_line

    def _write(self):
        with open(self.config_toml.config_file, "w") as toml_file:
            toml_file.write(self.new_content)

    def _reset(self):
        self.new_content = ""
        self.parameters_saved = []
