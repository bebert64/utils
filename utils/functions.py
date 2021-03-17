# -*- coding: utf-8 -*-

"""
Defines :
 The get_package_folder method.

 The get_data_folder method.

"""

import inspect
import pathlib
import sys
from typing import Any


def get_package_folder(my_object: Any) -> pathlib.Path:
    """
    The path to the package folder where the my_object is declared.

    If the package has been bundled in a .exe file, returns the application folder.
    The my_object can be anything : a class, a variable, a function...

    """
    if _is_application_frozen():
        package_path = _get_frozen_package_path()
    else:
        package_path = _get_unfrozen_package_path(my_object)
    return package_path


def _is_application_frozen() -> bool:
    return getattr(sys, "frozen", False)


def _get_frozen_package_path() -> pathlib.Path:
    exe_path = pathlib.Path(sys.executable)
    package_path = exe_path.parent
    return package_path


def _get_unfrozen_package_path(my_object: Any) -> pathlib.Path:
    my_object_file_path = _get_my_object_file_path(my_object)
    sub_package_path = my_object_file_path.parent
    package_path = sub_package_path.parent
    return package_path


def _get_my_object_file_path(my_object: Any) -> pathlib.Path:
    my_object_file = _get_my_object_file(my_object)
    my_object_file_path = pathlib.Path(my_object_file)
    return my_object_file_path


def _get_my_object_file(my_object: Any) -> str:
    my_object_module = inspect.getmodule(my_object)
    assert my_object_module is not None
    my_object_file = my_object_module.__file__
    return my_object_file


def get_data_folder(my_object: Any) -> pathlib.Path:
    """
    The path to the data folder for the package where my_object is declared.

    If the package has been bundled in a .exe file, returns the data folder of the
    application folder.
    The my_object can be anything : a class, a variable, a function...

    Warnings
    --------
    There is a strong assumption made here about where this data folder has to be. In
    the frozen case, we are looking for a sub-folder named "data" inside the folder
    where the .exe file is located. In the unfrozen case, it is assumed that the
    objects are always declared in a module in a sub-folder of the source folder,
    itself a sub-folder of the package general folder, and that this source folder is
    a sibling of the data folder.
    In other words, we need to have a structure like :
    package
        - data
        - source_code
            - app.py
            - sub-package 1
                - module 1.1
                - module 1.2
            - sub-package 2
                module 2.1
        etc...

    """
    package_folder = get_package_folder(my_object)
    if _is_application_frozen():
        data_folder = package_folder / "data"
    else:
        data_folder = package_folder.parent / "data"
    assert data_folder.exists()
    return data_folder
