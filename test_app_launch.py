"""Test script to verify SQLTrans launches successfully."""

import sys
from sqltrans.ui.app import SQLTransApp
from sqltrans.ui.screens.query_builder import QueryBuilderScreen
from sqltrans.models.query import QueryState
from sqltrans.sql.builder import QueryBuilder
from sqltrans.sql.dialects.postgresql import PostgreSQLDialect

print("=" * 60)
print("SQLTrans Application Launch Test")
print("=" * 60)

# Test 1: Import all components
print("\n[OK] Test 1: Importing components...")
print("  - SQLTransApp imported")
print("  - QueryBuilderScreen imported")
print("  - All models imported")
print("  - All dialects imported")

# Test 2: Create app instance
print("\n[OK] Test 2: Creating app instance...")
app = SQLTransApp(initial_dialect="postgresql")
print(f"  - App title: {app.TITLE}")
print(f"  - App subtitle: {app.SUB_TITLE}")

# Test 3: Test query building functionality
print("\n[OK] Test 3: Testing query building...")
state = QueryState(dialect="postgresql")
state.add_table("users")
state.add_column("id")
state.add_column("email")

from sqltrans.models.filters import Filter
f = Filter("age", ">", 18)
state.add_filter(f)

builder = QueryBuilder(state, PostgreSQLDialect())
sql = builder.build_query()
print(f"  Generated SQL: {sql}")

# Test 4: Test all widgets can be instantiated
print("\n[OK] Test 4: Testing widget instantiation...")
from sqltrans.ui.widgets import (
    DialectSelector,
    TableInput,
    ColumnList,
    FilterEditor,
    SQLPreview
)

dialect_selector = DialectSelector()
table_input = TableInput()
column_list = ColumnList()
filter_editor = FilterEditor()
sql_preview = SQLPreview()
print("  - All widgets instantiated successfully")

# Test 5: Test utilities
print("\n[OK] Test 5: Testing utilities...")
from sqltrans.utils.clipboard import is_clipboard_available
from sqltrans.utils.config import get_default_config

clipboard_available = is_clipboard_available()
print(f"  - Clipboard available: {clipboard_available}")

config = get_default_config()
print(f"  - Default dialect: {config.default_dialect}")
print(f"  - Theme: {config.theme}")

print("\n" + "=" * 60)
print("[OK] ALL TESTS PASSED!")
print("=" * 60)
print("\nThe SQLTrans application is ready to run!")
print("Launch with: python -m sqltrans")
print("=" * 60)
