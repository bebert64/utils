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
    name: str = peewee.CharField(primary_key=True)
    value: str = peewee.CharField()
    description: str = peewee.CharField()
    group: str = peewee.CharField()


class ConfigDatabase(Config):

    def __init__(self, ini_file):
        super().__init__(ini_file)
        self.database = self.get_database()
        Parameter._meta.database = self.database

    def get_database(self) -> peewee.SqliteDatabase:
        with open(self.config_file, "r") as ini_file:
            planning_db_path = pathlib.Path(ini_file.read().strip())
            database = peewee.SqliteDatabase(
                planning_db_path, pragmas={"foreign_keys": 1}
            )
        return database

    def load_data(self):
        for parameter in Parameter.select():
            json_value = json.loads(parameter.value)
            self._load_parameter(parameter.name, json_value)

    def save_data(self) -> None:
        for name, value in self.data.items():
            parameter = Parameter.get_or_create(name=name)[0]
            if isinstance(value, pathlib.Path):
                value = "PathObject:" + str(value)
            parameter.value = json.dumps(value)
            try:
                parameter.save(force_insert=True)
            except peewee.IntegrityError:
                parameter.save()
