# -*- coding: utf-8 -*-


"""
Extension of the xlwings library.

Defines :
 The get_workbook function

 The MyRange class

 The DataTable class

"""


from __future__ import annotations

from pathlib import Path
from typing import Optional, Dict, List, Iterator

import xlwings

from utils.my_types import (
    Row,
    Column,
    CellValue,
    DataRow,
    ExcelTable,
    ColumnFilter,
    Headers,
    Header,
)


def get_workbook(path: Path) -> xlwings.Book:
    """
    Returns the corresponding xlwings Excel workbook or create a new one.
    """
    workbook = _get_workbook_opened(path.stem)
    if workbook is None:
        workbook = _open_workbook(path)
    return workbook


def _get_workbook_opened(name: str) -> Optional[xlwings.Book]:
    """
    The first workbook found with 'name' in its name, None if nothing is found.
    """
    workbook_result = None
    for workbook in xlwings.books:
        if name == workbook.name:
            workbook_result = workbook
    return workbook_result


def _open_workbook(path: Path) -> xlwings.Book:
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


class MyRange(xlwings.Range):
    def __init__(self, *args, **kwargs):
        super().__init__(args, **kwargs)
        self.has_headers = True

    @staticmethod
    def cast(my_range: xlwings.Range, has_headers: bool = True) -> None:
        my_range.__class__ = MyRange
        my_range.has_headers = has_headers

    @property
    def first_row(self) -> Row:
        return self.row

    @property
    def first_column(self) -> Column:
        return self.column

    @property
    def last_row(self) -> Row:
        return self.last_cell.row

    @property
    def last_column(self) -> Column:
        return self.last_cell.column

    def get_headers(self) -> Optional[Headers]:
        if not self.has_headers:
            headers = None
        else:
            headers = [str(cell.value) for cell in self.rows[0]]
        return headers

    def cell(self, row_number: Row, column_number: Column) -> xlwings.Range:
        """The cell at the row and column relative to the first cell."""
        cell = self.rows[row_number - 1].columns[column_number - 1]
        return cell

    def get_column(self, header: str) -> xlwings.RangeColumns:
        if not self.has_headers:
            raise ValueError("Impossible to use get_column on a range without headers.")
        headers = self.get_headers()
        assert headers is not None
        if header not in headers:
            raise ValueError(f"{header} not found in the range headers ({headers})")
        column_index = headers.index(header)
        return self.columns[column_index]

    def create_table(self, autofit: bool = True) -> ExcelTable:
        """
        Creates a table fitting the range and returns it.

        Parameters
        ----------
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
        table_range = self.sheet.api.Range(self.address)
        table = self.sheet.api.ListObjects.Add(1, table_range, None, 1)
        if autofit:
            self.columns.autofit()
        return table

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
        xlwings_column = self.get_column(header)
        table.Sort.SortFields.Clear()
        if ascending:
            sort_order = 1
        else:
            sort_order = 2
        # The Key parameter needs a "real" Excel range (from the API) as value.
        # Using an "xlwings" range object will raise an error.
        table.Sort.SortFields.Add(
            Key=self.sheet.api.Range(xlwings_column.address), SortOn=0, Order=sort_order
        )
        table.Sort.MatchCase = False
        table.Sort.Apply()

    def get_data_table(
        self, headers: Headers = None, my_filter: ColumnFilter = None
    ) -> DataTable:
        self._check_headers(headers)
        if headers is None:
            headers = self.get_headers()
        assert headers is not None
        data_table = DataTable(headers)
        rows_filtered = self._rows_filtered(my_filter)
        for xlwings_row in rows_filtered:
            data_row = self.get_data_row(xlwings_row, headers=headers)
            data_table.add_row(data_row)
        return data_table

    def _check_headers(self, headers):
        if not self.has_headers:
            self._check_headers_length(headers)
        else:
            self._check_headers_subset(headers)

    def _check_headers_subset(self, headers):
        headers_set = set(headers)
        headers_range_set = set(self.get_headers())
        if not headers_set.issubset(headers_range_set):
            raise AssertionError(
                f"Some of the headers provided ({headers}) are not present on the "
                f"Excel file ({self.get_headers()})."
            )

    def _check_headers_length(self, headers):
        try:
            assert len(headers) == len(self.columns)
        except (TypeError, AssertionError) as err:
            raise AssertionError(
                f"The range has no header => get_data_table needs to have a "
                f"headers argument with the same length as the columns in the range "
                f"({len(self.column)})."
            ) from err

    def _rows_filtered(
        self, my_filter: Optional[ColumnFilter]
    ) -> Iterator[xlwings.RangeRows]:
        if my_filter is not None:
            rows_filtered = self._filter_rows(my_filter)
        else:
            first_data_row = 1 if self.has_headers else 0
            rows_filtered = self.rows[first_data_row:]
        return rows_filtered

    def _filter_rows(self, my_filter: ColumnFilter):
        if not self.has_headers:
            raise ValueError("Impossible to filter row on a range without headers.")
        headers = self.get_headers()
        assert headers is not None
        header, values = my_filter
        if header not in headers:
            raise ValueError(
                f"The header '{header}' has not been found in the range's headers "
                f"({headers})."
            )
        column_index = headers.index(header)
        for xlwings_row in self.rows:
            cell_filtered = xlwings_row[column_index]
            if cell_filtered.value in values:
                yield xlwings_row

    def get_data_row(
        self, xlwings_row: xlwings.RangeRows, headers: Headers = None
    ) -> DataRow:
        """
        A dictionary containing the row values.

        It is possible to filter on the columns to be included, both via the
        cols_included, ot the translation argument (more details provided in the
        Parameters section). If both arguments are provided, ValueError will be
        raised.

        Parameters
        ----------
        xlwings_row
            The number of the row which values we want.
        headers
            List of columns to be included in the results. Default is None, in
            which case all columns will be included.
        Returns
        -------
            A dictionary, which keys are the table header and which values
            are the ones found in the row.
        """
        self._check_headers(headers)
        if headers is None:
            headers = self.get_headers()
        assert headers is not None
        range_headers = self.get_headers() if self.has_headers else headers
        assert range_headers is not None
        data_row = {}
        if headers is None:
            headers = range_headers
        for header in headers:
            column_index = range_headers.index(header)
            data_row[header] = xlwings_row[column_index].value
        return data_row


class DataTable:
    def __init__(self, headers: List[str]) -> None:
        self.headers: List[str] = headers
        self.rows: List[List[CellValue]] = []

    def __getitem__(self, header: Header) -> List[CellValue]:
        column = self.headers.index(header)
        return [row[column] for row in self.rows]

    def add_row(self, data_row: DataRow) -> None:
        new_row: List[CellValue] = [None] * len(self.headers)
        for header, value in data_row.items():
            column = self.headers.index(header)
            new_row[column] = value
        self.rows.append(new_row)

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

    def dump_to_sheet(
        self,
        sheet: xlwings.Sheet,
        headers_excluded: Headers = None,
        first_row: Row = 1,
        first_column: Column = 1,
    ) -> None:
        """
        Dumps data into an Excel worksheet.

        The function should be used on an empty worksheet, as the data will be
        dumped at the beginning of the sheet without verifying if something is
        already there.

        Parameters
        ----------
        sheet

        headers_excluded
            A list of keys not to be dumped. Default is an empty list.
        first_row, first_column
            The coordinates of the first cell

        """
        column = first_column
        if headers_excluded is None:
            headers_excluded = []
        headers_included = [
            header for header in self.headers if header not in headers_excluded
        ]
        for header in headers_included:
            self._dump_column(sheet, header, first_row, column)

    def _dump_column(self, sheet, header, first_row, column):
        cell = sheet.range(first_row, column)
        cell.value = header
        for row in range(len(self.rows)):
            cell = sheet.range(first_row + 1 + row, column)
            cell.value = self[header][row]
        column += 1


# my_workbook = _get_workbook_opened("Classeur2")
# sheet = my_workbook.sheets[0]
# used_range = sheet.used_range
# MyRange.cast(used_range)
# my_filter = ("11", [92, 72, 42])
# print(used_range.get_data_table(headers=["11", "12", "a"]).rows)
# print(used_range.get_data_table(headers=["11", "12"], my_filter=my_filter).rows)
