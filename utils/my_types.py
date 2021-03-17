# -*- coding: utf-8 -*-

"""Defines types commonly used."""


from typing import Union, Dict, Tuple, List

import xlwings


Row = int
Column = int
CellValue = Union[int, str, None]
DataRow = Dict[str, CellValue]
ExcelTable = (
    xlwings._xlwindows.COMRetryObjectWrapper  # pylint: disable=protected-access
)
ColumnFilter = Tuple[int, List[CellValue]]
Header = str
Headers = List[str]
