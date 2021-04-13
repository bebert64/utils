# -*- coding: utf-8 -*-

"""
Defines :
 The MyCustomWidget class, a convenience base class with generic functions. The derived
 class must also inherit from a QtWidgets.QWidget.

"""

from __future__ import annotations

import re
from functools import wraps
from pathlib import Path
from typing import Optional, Type, TypeVar, Callable, Any

from PySide6 import QtCore, QtUiTools, QtWidgets

from utils.functions import get_data_folder

MyType = TypeVar("MyType")


class MyThread(QtCore.QThread):

    """
    A QThread executing a function and capable of updating a message box.

    Parameters
    ----------
    parent: QtWidgets.QWidget
        The parent object, which might itself be a ShortCutsChild, or the
        first ancestor, which has to be the Main Window.
    func: Callable
        The function meant to be run in the separate thread.
        args
    *args: Any
        Variable length argument list, required to run the function.
    **kwargs: Any
        Arbitrary keyword arguments, required to run the function.
    """

    update_message: QtCore.Signal = QtCore.Signal(str)
    """
    A signal sent to update the message in the associated message box.
    """

    update_title: QtCore.Signal = QtCore.Signal(str)
    """
    A signal sent to update the title of the associated message box.
    """

    finished: QtCore.Signal = QtCore.Signal()
    """
    A signal sent when the function has finished running.
    """

    def __init__(
        self, parent: QtWidgets.QWidget, func: Callable, *args: Any, **kwargs: Any
    ) -> None:
        super().__init__(parent)
        self.func = func
        self.args = args
        self.kwargs = kwargs

    def run(self) -> None:
        """
        Executes the function and signals the end.
        """
        self.func(self.parent(), *self.args, **self.kwargs)
        self.finished.emit()  # type: ignore


class MyCustomWidget:

    """
    A convenience class to create QT object from .ui files.

    MyCustomWidget is meant to be inherited, and cannot be used by itself. The derived
    class must also inherit from a QtWidgets.QWidget.

    Class Attributes
    ----------------
    ui_file_name
    ui_folder_path

    Class Methods
    -------------
    create_widget

    """

    _additional_docstring: str = """
    Warning
    -------
    This widget should not be instantiated directly, but rather through the factory
    method create_my_main_window.

    """

    _loader: QtUiTools.QUiLoader

    ui_file_name: str
    """
    The name of the gui file to use. If ui_file_name is not initialized by the
    derived class, the loader will try to read from a .ui file with the same
    base name as the class itself, converted from CamelCase to snake_case.
    Ex: for MainWidget, the loader will try to load main_widget.ui.
    """

    ui_folder_path: Path
    """
    The path to the folder in which to find the .ui files. If not provided by the
    derived class, the "ui_files" sub-folder of the data folder for the package where
    the class is defined will be used.
    """

    # def __init__(self) -> None:
    #     self.my_thread: Optional[MyThread] = None
    #     self.msg_box: Optional[MyMsgBox] = None

    @classmethod
    def create_widget(
        cls, parent: Optional[QtWidgets.QWidget] = None
    ) -> MyCustomWidget:
        """Factory method to create a MyCustomWidget."""
        # create_widget is (part of) a factory method, and should therefore be allowed
        # to access protected members of the class.
        # pylint: disable=protected-access
        widget = cls._create_widget_using_loader(parent)
        assert isinstance(widget, cls)
        assert isinstance(widget, QtWidgets.QWidget)
        return widget

    def _has_parent(self) -> bool:
        assert isinstance(self, QtWidgets.QWidget)
        parent = self.parent()  # pylint: disable=no-member
        return parent is not None

    @classmethod
    def _create_widget_using_loader(
        cls, parent: Optional[QtWidgets.QWidget]
    ) -> MyCustomWidget:
        loader = cls._get_loader()
        ui_file = cls._get_ui_file()
        widget = cls._create_new_widget_from_ui_file(loader, parent, ui_file)
        return widget

    @staticmethod
    def _create_new_widget_from_ui_file(
        loader: QtUiTools.QUiLoader,
        parent: Optional[QtWidgets.QWidget],
        ui_file: QtCore.QFile,
    ) -> QtWidgets.QWidget:
        ui_file.open(QtCore.QFile.ReadOnly)
        widget = loader.load(ui_file, parent)
        ui_file.close()
        return widget

    @classmethod
    def _get_loader(cls) -> QtUiTools.QUiLoader:
        if not hasattr(cls, "_loader"):
            cls._loader = QtUiTools.QUiLoader()
            cls._loader.registerCustomWidget(cls)
        return cls._loader

    @classmethod
    def _get_ui_file(cls) -> QtCore.QFile:
        ui_file_name = cls._get_ui_file_name()
        ui_folder_path = cls._get_ui_folder_path()
        ui_file = QtCore.QFile(str(ui_folder_path / ui_file_name))
        return ui_file

    @classmethod
    def _get_ui_file_name(cls) -> str:
        if hasattr(cls, "ui_file_name"):
            ui_file_name = cls.ui_file_name
        else:
            ui_file_name = cls._get_ui_file_name_default()
        return ui_file_name

    @classmethod
    def _get_ui_file_name_default(cls) -> str:
        class_name = cls.__name__
        ui_file_name = cls._camel_case_to_snake_case(class_name) + ".ui"
        return ui_file_name

    @classmethod
    def _get_ui_folder_path(cls) -> Path:
        if hasattr(cls, "ui_folder_path"):
            ui_folder_path = cls.ui_folder_path
        else:
            ui_folder_path = cls._get_ui_folder_path_default()
        return ui_folder_path

    @classmethod
    def _get_ui_folder_path_default(cls) -> Path:
        data_folder = get_data_folder(cls)
        ui_folder = data_folder / "ui_files"
        return ui_folder

    def _copy_attribute_from_parent(self, attribute_name: str) -> None:
        assert isinstance(self, QtWidgets.QWidget)
        parent = self.parent()  # pylint: disable=no-member
        if hasattr(parent, attribute_name):
            attribute_value = getattr(parent, attribute_name)
            setattr(self, attribute_name, attribute_value)

    def get_ancestor_by_class(self, ancestor_class: Type[MyType]) -> Optional[MyType]:
        """
        Gets the closest ancestor of the given class.

        Parameters
        ----------
        ancestor_class
            The class of the ancestor to look for. If no class is given, the parent is
            returned.

        Returns
        -------
        Optional[ancestor_class]
            The closest matching ancestor, or None if no ancestor is found.

        """
        # pylint: disable=no-member
        assert isinstance(self, QtWidgets.QWidget)
        parent = self.parent()
        while not (isinstance(parent, ancestor_class) or parent is None):
            parent = parent.parent()
        return parent

    def get_main_window(self) -> Optional[QtWidgets.QMainWindow]:
        """Returns the closest :class:`QMainWindow` (there should be only one)."""
        return self.get_ancestor_by_class(QtWidgets.QMainWindow)

    @staticmethod
    def _camel_case_to_snake_case(name: str) -> str:
        return re.sub(r"(?<!^)(?=[A-Z])", "_", name).lower()

    @staticmethod
    def display_msg_box(title: str, msg: str) -> None:
        """Creates a simple message box."""
        msg_box = QtWidgets.QMessageBox()
        msg_box.setWindowTitle(title)
        msg_box.setText(msg)
        msg_box.exec_()

    def set_msg_box_message(self, msg: str) -> None:
        """
        Sets the title of the message box linked to the thread.

        Warning
        -------
        This methods needs the my_thread and my_msg_box attributes of the widget
        to hve been initialized, and should only be used inside a method wrapped
        with display_info_while_running.

        """
        if self.my_thread is not None:
            self.my_thread.update_message.emit(msg)  # type: ignore

    def set_msg_box_title(self, title: str) -> None:
        """
        Sets the message inside of the message box linked to the thread.

        Warning
        -------
        This methods needs the my_thread and my_msg_box attributes of the widget
        to hve been initialized, and should only be used inside a method wrapped
        with display_info_while_running.

        """
        if self.my_thread is not None:
            self.my_thread.update_title.emit(title)  # type: ignore

    def handle_thread_finished(self) -> None:
        """
        Changes the button of the message box to OK.

        The behaviour of the button also changes, from terminating the
        running thread to simply closing the message box.
        """
        assert self.msg_box is not None
        self.msg_box.pushButton.setText("OK")
        self.msg_box.pushButton.clicked.connect(self.msg_box.close)

    def cancel_thread(self) -> None:
        """
        Cancels the thread and closes the message box.
        """
        assert self.my_thread is not None
        assert self.msg_box is not None
        self.my_thread.terminate()
        self.msg_box.close()


class MyMsgBox(QtWidgets.QDialog, MyCustomWidget):

    """
    A simple message box.

    Warning
    -------
    This widget should not be instantiated directly, but rather through the
    factory method create_msg_box.

    """

    @classmethod
    def create_msg_box(cls) -> MyCustomWidget:
        """Factory method to create a MyMsgBox. """
        msg_box = cls.create_widget()
        assert isinstance(msg_box, QtWidgets.QDialog)
        msg_box.setWindowFlags(
            QtCore.Qt.WindowSystemMenuHint | QtCore.Qt.WindowTitleHint
        )
        return msg_box


def display_info_while_running(func: Callable) -> Callable:
    """
    Decorator to facilitate the use of threading and displaying information.

    Executes the function in a separate thread and displays information about the
    execution status (or anything else) in a message box.
    """

    @wraps(func)
    def wrapper(self: Any, *args: Any, **kwargs: Any) -> None:
        """
        Wrapper for the function.
        """
        self.msg_box = MyMsgBox.create_msg_box()
        self.my_thread = MyThread(self, func, *args, **kwargs)
        self.my_thread.update_message.connect(self.msg_box.label.setText)  # type: ignore
        self.my_thread.update_title.connect(self.msg_box.setWindowTitle)  # type: ignore
        self.my_thread.finished.connect(self.handle_thread_finished)  # type: ignore
        self.msg_box.pushButton.clicked.connect(self.cancel_thread)
        self.my_thread.start()
        self.msg_box.exec_()

    return wrapper
