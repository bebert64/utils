# -*- coding: utf-8 -*-

"""
Defines types commonly used.

 Row: int

 Column: int

 CellValue: int, str, or None

 DataRow: Dict[str, CellValue]. A row of data in an Excel table

 ColumnFilter: a tuple of a column number and a list of CellValue

 Header: str

 Headers: a list of Header

 Pixel: int

"""


from typing import Union, Dict, Tuple, List

Row = int
Column = int
CellValue = Union[int, str, None]
Header = str
Headers = List[Header]
ColumnFilter = Tuple[Header, List[CellValue]]
DataRow = Dict[Header, CellValue]
Pixel = int
