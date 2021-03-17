# -*- coding: utf-8 -*-


"""
Extension of the xlwings library.

Defines a MySheet class, extending the xlwings.Sheet object, and three methods
an xlwings.Workbook : get_wb_by_name, get_wb_by_path and get_wb. The third one
is a "combination" of the first two.
"""


from __future__ import annotations

from pathlib import Path
from typing import Optional, Dict, Iterable, List

import xlwings

from utils.my_types import (
    Row,
    Column,
    CellValue,
    DataRow,
    ExcelTable,
    ColumnFilter,
    Headers,
)


class MySheet:

    """
    An extension of the xlwings.Sheet object.

    Parameters
    ----------
    sheet
        The xlwings.Sheet object that will be extended.
    """

    def __init__(self, sheet: xlwings.Sheet):
        self.sheet: xlwings.Sheet = sheet
        self.used_range: MyRange = MyRange(self.sheet.used_range)

    def cell(self, row: Row, column: Column) -> xlwings.main.Range:
        """The value from the cell at row 'row' and column 'col'."""
        return self.sheet.range((row, column))

    def cell_value(self, row: Row, column: Column) -> CellValue:
        """The value from the cell at row 'row' and column 'col'."""
        cell = self.cell(row, column)
        return cell.value

    def rows(
        self, exclude_header: bool = False, my_filter: ColumnFilter = None
    ) -> Iterable[Row]:
        """Yields the rows number from used range."""
        if exclude_header:
            first_row = 2
        else:
            first_row = 1
        for row in range(first_row, self.sheet.used_range.last_cell.row + 1):
            if my_filter is not None:
                column, values = my_filter
                if self.cell_value(row, column) in values:
                    yield row
            else:
                yield row

    def columns(self) -> Iterable[Column]:
        """Yields the columns number from used range."""
        for column in range(1, self.sheet.used_range.last_cell.column + 1):
            yield column

    def dump_data(
        self,
        data_table: DataTable,
        headers_excluded: List[str] = None,
        first_row: int = 1,
        first_column: int = 1,
    ) -> None:
        """
        Dumps data into an Excel worksheet.

        The function should be used on an empty worksheet, as the data will be
        dumped at the beginning of the sheet without verifying if something is
        already there.

        Parameters
        ----------
        data_table
            A list of dict, with identical keys. The keys will be used as header
            for the columns on the first row, and the values will be dumped into
            successive rows.
        headers_excluded
            A list of keys NOT to be dumped. Default is an empty list.
        """
        column = first_column
        if headers_excluded is None:
            headers_excluded = []
        for header in data_table.headers:
            if header not in headers_excluded:
                self.cell(first_row, column).value = header
                for row in range(len(data_table.rows)):
                    self.cell(first_row + 1 + row, column).value = data_table[header][
                        row
                    ]
                column += 1

    def order_table(
        self, table: ExcelTable, header: str, ascending: bool = True
    ) -> None:
        """
        Orders the rows of a table by field name.

        Parameters
        ----------
        table
            The table to be ordered. The table needs to have header in its first
            row.
        header
            The header for the column used for ordering the rows.
        ascending
            If True, rows will be ordered in ascending order. If False, rows will
            be ordered in descending order. Default is True.
        """
        column = self.get_column(table, header)
        if column is not None:
            table.Sort.SortFields.Clear()
            if ascending:
                sort_order = 1
            else:
                sort_order = 2

            # The Key parameter needs a "real" Excel range (from the API) as value.
            # Using an "xlwings" range object will raise an error.
            table.Sort.SortFields.Add(
                Key=self.sheet.api.Range(column.address), SortOn=0, Order=sort_order
            )
            table.Header = 1
            table.Sort.MatchCase = False
            table.Sort.Apply()

    def get_column(
        self, table: ExcelTable, header: str
    ) -> Optional[xlwings.main.Range]:
        """
        The "xlwings" columns object from 'table' which header is 'field'.

        Parameters
        ----------
        table
            An Excel object (as created by the API), representing the table in
            which we are looking for field.
        header
            The field we are looking for in the table's header.

        Returns
        ------
        xlwings.column
            An xlwing column object representing the column found, or None if the
            field is not found in the table header.
        """
        xlwings_range = self.sheet.range(table.Range.Address)
        row = xlwings_range.rows[0].row
        for xlwings_column in xlwings_range.columns:
            if self.cell_value(row, xlwings_column.column) == header:
                return xlwings_column
        return None


class DataTable:
    def __init__(self, headers: List[str]) -> None:
        self.headers: List[str] = headers
        self.rows: List[List[CellValue]] = []

    def add_row(self, data_row: DataRow) -> None:
        new_row: List[CellValue] = [None] * len(self.headers)
        for header, value in data_row.items():
            column = self.headers.index(header)
            new_row[column] = value
        self.rows.append(new_row)

    def __getitem__(self, header):
        column = self.headers.index(header)
        return [row[column] for row in self.rows]

    def get_data_row(self, row: int) -> DataRow:
        data_row = {}
        for header in self.headers:
            data_row[header] = self[header][row]
        return data_row

    def translate(self, translation: Dict[str, str]) -> None:
        new_headers = []
        for header in self.headers:
            try:
                new_headers.append(translation[header])
            except KeyError:
                new_headers.append(header)
        self.headers = new_headers


class MyRange:
    def __init__(
        self,
        my_range: xlwings.Range,
        has_headers: bool = True,
        headers: List[str] = None,
    ):
        self.range: xlwings.Range = my_range
        if has_headers:
            self.headers: List[str] = self.get_headers()
        else:
            self.headers = headers

    @property
    def first_row(self) -> Row:
        return self.range.row

    @property
    def first_column(self) -> Column:
        return self.range.column

    @property
    def last_row(self) -> Row:
        return self.range.last_cell.row

    @property
    def last_column(self) -> Column:
        return self.range.last_cell.column

    def get_headers(self) -> Headers:
        headers = []
        columns_quantity = self.last_column - self.first_column + 1
        for column in range(columns_quantity):
            headers.append(self.range.columns[column].rows[0].value)
        return headers

    def cell_value(self, row: Row, column: Column) -> CellValue:
        """The value from the cell at row 'row' and column 'col'."""
        cell = self.range.rows[row - 1].columns[column - 1]
        return cell.value

    def rows(
        self, exclude_header: bool = False, my_filter: ColumnFilter = None
    ) -> Iterable[Row]:
        """Yields the rows number from used range."""
        if exclude_header:
            first_row = 2
        else:
            first_row = 1
        for row in range(first_row, self.last_row + 1):
            if my_filter is not None:
                column, values = my_filter
                if self.cell_value(row, column) in values:
                    yield row
            else:
                yield row

    def columns(self) -> Iterable[Column]:
        """Yields the columns number from used range."""
        for column in range(self.first_column, self.last_column + 1):
            yield column

    def create_table(self, autofit: bool = True) -> ExcelTable:
        """
        Creates a table including the range rng and returns it.

        Parameters
        ----------
        rng
            The range used to create the table
        autofit
            If True, the table's columns width will be adapted to the content.
            Default is True.

        Returns
        -------
        Excel table:
            The table created. The object returned is created by the api, and
            is a "real" Excel object, not an "xlwings" object.
        """
        # To create a table, we need a "real" Excel range, as provided by the API.
        # Using an "xlwings" range object will raise an Error.
        table_range = self.range.sheet.api.Range(self.range.address)
        table = self.range.sheet.api.ListObjects.Add(1, table_range, None, 1)
        if autofit:
            self.range.columns.autofit()
        return table

    def get_data_row(self, row: Row, headers_included: Headers = None) -> DataRow:
        """
        A dictionary containing the row values.

        It is possible to filter on the columns to be included, both via the
        cols_included, ot the translation argument (more details provided in the
        Parameters section). If both arguments are provided, ValueError will be
        raised.

        Parameters
        ----------
        row
            The number of the row which values we want.
        headers_included
            List of columns to be included in the results. Default is None, in
            which case all columns will be included.
        Returns
        -------
            A dictionary, which keys are the table header (or their translation
            if the translation argument has been provided), and which values
            are the ones found in the row.
        """
        if self.headers is None:
            raise ValueError
        data_row = {}
        if headers_included is None:
            headers_included = self.headers
        for header in headers_included:
            column = self.headers.index(header) + 1
            data_row[header] = self.cell_value(row, column)
        return data_row

    def get_data_table(
        self, headers_included: Headers = None, my_filter: ColumnFilter = None
    ) -> DataTable:
        if self.headers is None:
            raise ValueError
        if headers_included is None:
            headers_included = self.headers
        data_table = DataTable(headers_included)
        for row in self.rows(exclude_header=True, my_filter=my_filter):
            data_row = self.get_data_row(row, headers_included=headers_included)
            data_table.add_row(data_row)
        return data_table


def get_workbook_opened(name: str) -> Optional[xlwings.Book]:
    """
    The first workbook found with 'name' in its name, None if nothing is found.
    """
    workbook_result = None
    for workbook in xlwings.books:
        if name == workbook.name:
            workbook_result = workbook
    return workbook_result


def open_workbook(path: Path) -> xlwings.Book:
    """
    Opens the corresponding xlwings Excel workbook.

    Only works if the workbook is not already opened. If the path doesn't already
    exists, a new book is created and saved at that path.

    """
    if path.exists():
        workbook = xlwings.Book(path.absolute())
    else:
        workbook = xlwings.Book()
        workbook.save(path)
    return workbook


def get_workbook(path: Path) -> xlwings.Book:
    """
    Returns the corresponding xlwings Excel workbook or create a new one.
    """
    workbook = get_workbook_opened(path.stem)
    if workbook is None:
        workbook = open_workbook(path)
    return workbook
