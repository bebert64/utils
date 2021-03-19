# -*- coding: utf-8 -*-

"""
Defines :
 The ConfigDatabase class, derived from Config

"""


import json
import pathlib

import peewee

from utils.config import Config


class Parameter(peewee.Model):
    """A parameter meant to be accessed through a ConfigDatabase instance."""

    name: str = peewee.CharField(primary_key=True)
    value: str = peewee.CharField()
    description: str = peewee.CharField()
    group: str = peewee.CharField()


class ConfigDatabase(Config):

    """
    Class derived from Config, specific to information being stored in a .toml file.

    Warning
    -------
    The class should not be instantiated directly, but rather through the Config.create
    factory method, that will return the appropriate derived class (depending on the
    type of file holding those parameters).

    """

    def __init__(self, ini_file: pathlib.Path) -> None:
        super().__init__(ini_file)
        self.database = self._get_database()
        Parameter._meta.database = self.database  # pylint: disable=no-member

    def _get_database(self) -> peewee.SqliteDatabase:
        with open(self.config_file, "r") as ini_file:
            planning_db_path = pathlib.Path(ini_file.read().strip())
            database = peewee.SqliteDatabase(
                planning_db_path, pragmas={"foreign_keys": 1}
            )
        return database

    def load(self) -> None:
        """Loads values from the sqlite database."""
        for parameter in Parameter.select():
            json_value = json.loads(parameter.value)
            self._load_parameter(parameter.name, json_value)

    def save(self) -> None:
        """Saves values to the sqlite database."""
        for name, value in self.data.items():
            parameter = Parameter.get_or_create(name=name)[0]
            value = self._translate_value(value)
            parameter.value = json.dumps(value)
            try:
                parameter.save(force_insert=True)
            except peewee.IntegrityError:
                parameter.save()
