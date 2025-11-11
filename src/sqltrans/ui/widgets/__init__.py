"""UI widgets for SQLTrans."""

from sqltrans.ui.widgets.dialect_selector import DialectSelector
from sqltrans.ui.widgets.table_input import TableInput
from sqltrans.ui.widgets.column_list import ColumnList
from sqltrans.ui.widgets.filter_editor import FilterEditor
from sqltrans.ui.widgets.sql_preview import SQLPreview

__all__ = [
    "DialectSelector",
    "TableInput",
    "ColumnList",
    "FilterEditor",
    "SQLPreview",
]
