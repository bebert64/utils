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


def get_data_folder(my_object: Any = None) -> pathlib.Path:
    """
    The path to the data folder for my_object.

    The data folder is defined as a "sibling" folder (named "data") to the package
    folder where my_object is defined. More information is available in the
    get_package_folder documentation.
    If no my_object is passed, returns the data folder for the package from where
    the function is called.

    """
    package_folder = get_package_folder(my_object)
    if _is_application_frozen():
        data_folder = package_folder / "data"
    else:
        data_folder = package_folder.parent / "data"
    assert data_folder.exists()
    return data_folder


def get_package_folder(my_object: Any = None) -> pathlib.Path:
    """
    The path to the package folder from where the function is called, or where
    my_object is declared.

    If the package has been bundled in a .exe file, returns the data folder of the
    application itself. Otherwise, the package folder is defined as the highest folder
    in the folder structure containing an __init__.py file.

    Parameters
    ----------
    my_object
        If needed, one can pass as an argument an object defined in an imported module
        or package. The package folder returned will then be the one from the package
        where my_object is defined, which will be different to the one from where the
        function is called.
        my_object can be anything : a class, a variable, a function...

    Warnings
    --------
    There is a strong assumption about the code structure. In the unfrozen case, it is
    assumed that all package and sub-package have an __init__.py file.

    - package
        - data
        - source_code
            - __init__.py
            - app.py
            - sub-package 1
               - __init__.py
               - module 1.1
               - module 1.2
            - sub-package 2
               - __init__.py
               - module 2.1

    In this example, the package folder is "source_code".
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
    if my_object is None:
        package_path = _get_package_folder_from_caller()
    else:
        package_path = _get_my_object_file(my_object)
    while _is_parent_a_package(package_path):
        package_path = package_path.parent
    return package_path


def _get_package_folder_from_caller():
    index = 0
    caller = inspect.stack()[index].filename
    while caller == __file__:
        index += 1
        caller = inspect.stack()[index].filename
    return pathlib.Path(caller)


def _is_parent_a_package(package_path: pathlib.Path) -> bool:
    parent_path = package_path.parent
    init_file = parent_path / "__init__.py"
    return init_file.exists()


def _get_my_object_file(my_object: Any) -> pathlib.Path:
    my_object_module = inspect.getmodule(my_object)
    assert my_object_module is not None
    my_object_file = my_object_module.__file__
    my_object_file_path = pathlib.Path(my_object_file)
    package_path = my_object_file_path.parent
    return package_path
