"""SQL query builder for generating SQL from QueryState."""

from sqltrans.models.query import QueryState
from sqltrans.sql.dialects.base import BaseDialect
from sqltrans.utils.logging import get_logger

logger = get_logger("sqltrans.sql.builder")


class QueryBuilder:
    """Build SQL SELECT queries from QueryState using a specific dialect.

    The QueryBuilder takes a QueryState (containing table, columns, filters,
    and dialect) and generates proper SQL using the appropriate SQL dialect
    for escaping and formatting.

    Responsibilities:
    - Generate SELECT clause with quoted column names
    - Generate FROM clause with quoted table name
    - Generate WHERE clause from filters
    - Assemble complete SQL query
    - Validate state before building

    Example:
        >>> from sqltrans.models.query import QueryState
        >>> from sqltrans.sql.dialects.postgresql import PostgreSQLDialect
        >>> state = QueryState(dialect="postgresql")
        >>> state.add_table("users")
        >>> state.add_column("id")
        >>> state.add_column("name")
        >>> builder = QueryBuilder(state, PostgreSQLDialect())
        >>> sql = builder.build_query()
        >>> print(sql)
        SELECT "id", "name" FROM "users"
    """

    def __init__(self, state: QueryState, dialect: BaseDialect):
        """Initialize QueryBuilder with state and dialect.

        Args:
            state: QueryState containing query information
            dialect: SQL dialect for proper escaping and formatting

        Example:
            >>> state = QueryState()
            >>> dialect = PostgreSQLDialect()
            >>> builder = QueryBuilder(state, dialect)
        """
        self.state = state
        self.dialect = dialect

    def build_select(self) -> str:
        """Build the SELECT clause.

        Generates a SELECT clause with quoted column names. If no columns
        are specified, returns "SELECT *" to select all columns.

        Returns:
            SELECT clause string (e.g., 'SELECT "id", "name"' or 'SELECT *')

        Example:
            >>> state = QueryState()
            >>> state.add_column("id")
            >>> state.add_column("email")
            >>> builder = QueryBuilder(state, PostgreSQLDialect())
            >>> builder.build_select()
            'SELECT "id", "email"'

        Notes:
            - Empty columns list results in SELECT *
            - Column names are quoted using dialect.quote_identifier()
            - Columns are comma-separated
        """
        if not self.state.columns:
            return "SELECT *"

        # Quote each column name and join with commas
        quoted_columns = [
            self.dialect.quote_identifier(col) for col in self.state.columns
        ]
        return f"SELECT {', '.join(quoted_columns)}"

    def build_from(self) -> str:
        """Build the FROM clause.

        Generates a FROM clause with the quoted table name.

        Returns:
            FROM clause string (e.g., 'FROM "users"')

        Raises:
            ValueError: If table is not set in state

        Example:
            >>> state = QueryState()
            >>> state.add_table("customers")
            >>> builder = QueryBuilder(state, PostgreSQLDialect())
            >>> builder.build_from()
            'FROM "customers"'

        Notes:
            - Table name is quoted using dialect.quote_identifier()
            - Raises error if no table is set
        """
        if not self.state.table:
            raise ValueError("Cannot build FROM clause without a table")

        quoted_table = self.dialect.quote_identifier(self.state.table)
        return f"FROM {quoted_table}"

    def build_where(self) -> str:
        """Build the WHERE clause from filters.

        Generates a WHERE clause by converting each filter to SQL and
        combining them with AND. Returns empty string if no filters.

        Returns:
            WHERE clause string (e.g., 'WHERE "age" > 18 AND "status" = \'active\'')
            or empty string if no filters

        Example:
            >>> from sqltrans.models.filters import Filter
            >>> state = QueryState()
            >>> state.add_filter(Filter("age", ">", 18))
            >>> state.add_filter(Filter("status", "=", "active"))
            >>> builder = QueryBuilder(state, PostgreSQLDialect())
            >>> builder.build_where()
            'WHERE "age" > 18 AND "status" = \\'active\\''

        Notes:
            - Each filter is converted to SQL using filter.to_sql(dialect)
            - Multiple filters are combined with AND
            - Returns empty string if no filters (no WHERE clause)
        """
        if not self.state.filters:
            return ""

        # Convert each filter to SQL condition
        conditions = [f.to_sql(self.dialect) for f in self.state.filters]

        # Join with AND
        where_conditions = " AND ".join(conditions)
        return f"WHERE {where_conditions}"

    def build_query(self) -> str:
        """Build complete SQL SELECT query.

        Assembles the complete SQL query from SELECT, FROM, and WHERE clauses.

        Returns:
            Complete SQL query string

        Raises:
            ValueError: If table is not set in state

        Example:
            >>> from sqltrans.models.query import QueryState
            >>> from sqltrans.models.filters import Filter
            >>> state = QueryState()
            >>> state.add_table("orders")
            >>> state.add_column("id")
            >>> state.add_column("total")
            >>> state.add_filter(Filter("status", "=", "paid"))
            >>> builder = QueryBuilder(state, PostgreSQLDialect())
            >>> builder.build_query()
            'SELECT "id", "total" FROM "orders" WHERE "status" = \\'paid\\''

        Notes:
            - Validates that table is set before building
            - SELECT clause is always included
            - FROM clause is always included (requires table)
            - WHERE clause is optional (only if filters exist)
            - Clauses are space-separated
        """
        # Validate state
        if not self.state.table:
            logger.error("Attempted to build query without table name")
            raise ValueError("Cannot build query without a table name")

        try:
            logger.debug(f"Building query for table '{self.state.table}' with {len(self.state.columns)} columns and {len(self.state.filters)} filters")

            # Build each clause
            select_clause = self.build_select()
            from_clause = self.build_from()
            where_clause = self.build_where()

            # Assemble query
            query_parts = [select_clause, from_clause]

            if where_clause:
                query_parts.append(where_clause)

            query = " ".join(query_parts)
            logger.info(f"Successfully built query: {query[:100]}...")
            return query

        except Exception as e:
            logger.error(f"Error building query: {e}", exc_info=True)
            raise

    def __repr__(self) -> str:
        """Return string representation for debugging.

        Returns:
            String representation of QueryBuilder

        Example:
            >>> builder = QueryBuilder(QueryState(), PostgreSQLDialect())
            >>> repr(builder)
            'QueryBuilder(state=QueryState(...), dialect=PostgreSQLDialect(...))'
        """
        return f"QueryBuilder(state={self.state!r}, dialect={self.dialect!r})"
