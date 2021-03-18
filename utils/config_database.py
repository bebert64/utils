import json
import pathlib
from typing import Any

import peewee

from utils.config import Config


class ConfigDatabase(Config):

    class Parameter(peewee.Model):
        name: str = peewee.CharField(primary_key=True)
        value: str = peewee.CharField()
        description: str = peewee.CharField()
        group: str = peewee.CharField()

    def __init__(self, ini_file):
        self.database = self.get_database(ini_file)
        ConfigDatabase.Parameter._meta.database = self.database

    def get_database(self, ini_file_path: pathlib.Path) -> peewee.SqliteDatabase:
        with open(ini_file_path, "r") as ini_file:
            planning_db_path = pathlib.Path(ini_file.read().strip())
            database = peewee.SqliteDatabase(planning_db_path, pragmas={"foreign_keys": 1})
        return database

    def __getitem__(self, name: str):
        parameter = ConfigDatabase.Parameter.get(name=name)
        json_value = json.loads(parameter.value)
        if isinstance(json_value, str) and json_value.startswith("PathObject:"):
            path_as_string = json_value[len("PathObject:"):]
            json_value = pathlib.Path(path_as_string)
        return json_value

    def __setitem__(self, name: str, value: Any) -> None:
        parameter = ConfigDatabase.Parameter.get_or_create(name=name)[0]
        if isinstance(value, pathlib.Path):
            value = "PathObject:" + str(value)
        parameter.value = json.dumps(value)
        try:
            parameter.save(force_insert=True)
        except peewee.IntegrityError:
            parameter.save()
