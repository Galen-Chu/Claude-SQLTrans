/**
 * SQLTrans Web GUI - Main Application
 * Coordinates between API, UI, and user interactions
 */

class SQLTransApp {
    constructor() {
        this.state = {
            table: null,
            columns: [],
            filters: [],
            dialect: 'generic',
            sql: ''
        };

        this.elements = {};
        this.init();
    }

    /**
     * Initialize the application
     */
    async init() {
        this.cacheElements();
        this.attachEventListeners();
        await this.loadInitialState();
        console.log('SQLTrans Web GUI initialized');
    }

    /**
     * Cache DOM elements for performance
     */
    cacheElements() {
        this.elements = {
            dialectSelect: document.getElementById('dialect-select'),
            tableInput: document.getElementById('table-input'),
            columnInput: document.getElementById('column-input'),
            addColumnBtn: document.getElementById('add-column-btn'),
            filterColumn: document.getElementById('filter-column'),
            filterOperator: document.getElementById('filter-operator'),
            filterValue: document.getElementById('filter-value'),
            addFilterBtn: document.getElementById('add-filter-btn'),
            clearQueryBtn: document.getElementById('clear-query-btn'),
            copyBtn: document.getElementById('copy-btn'),
            downloadBtn: document.getElementById('download-btn'),
        };
    }

    /**
     * Attach all event listeners
     */
    attachEventListeners() {
        // Dialect selector
        this.elements.dialectSelect.addEventListener('change', (e) => this.handleDialectChange(e));

        // Table input
        this.elements.tableInput.addEventListener('blur', (e) => this.handleTableChange(e));
        this.elements.tableInput.addEventListener('keypress', (e) => {
            if (e.key === 'Enter') {
                e.target.blur();
            }
        });

        // Column input
        this.elements.addColumnBtn.addEventListener('click', () => this.handleAddColumn());
        this.elements.columnInput.addEventListener('keypress', (e) => {
            if (e.key === 'Enter') {
                e.preventDefault();
                this.handleAddColumn();
            }
        });

        // Filter input
        this.elements.addFilterBtn.addEventListener('click', () => this.handleAddFilter());
        this.elements.filterOperator.addEventListener('change', () => this.handleOperatorChange());
        
        // Enter key on filter inputs
        [this.elements.filterColumn, this.elements.filterValue].forEach(input => {
            input.addEventListener('keypress', (e) => {
                if (e.key === 'Enter') {
                    e.preventDefault();
                    this.handleAddFilter();
                }
            });
        });

        // Clear query
        this.elements.clearQueryBtn.addEventListener('click', () => this.handleClearQuery());

        // Copy and download
        this.elements.copyBtn.addEventListener('click', () => this.handleCopy());
        this.elements.downloadBtn.addEventListener('click', () => this.handleDownload());
    }

    /**
     * Load initial state from backend
     */
    async loadInitialState() {
        try {
            const state = await api.getQueryState();
            this.state = state;
            this.renderState();
            await this.updateSQLPreview();
        } catch (error) {
            Toast.error('Failed to load initial state');
            console.error(error);
        }
    }

    /**
     * Handle dialect change
     */
    async handleDialectChange(e) {
        const dialect = e.target.value;

        try {
            InputValidator.clearAllErrors();
            const result = await api.setDialect(dialect);
            this.state.dialect = result.dialect;
            
            if (result.sql !== undefined) {
                this.state.sql = result.formatted || result.sql;
                await SQLDisplay.update(this.state.sql);
            }

            Toast.success(`Dialect changed to ${dialect}`);
        } catch (error) {
            Toast.error(error.message);
            e.target.value = this.state.dialect;
        }
    }

    /**
     * Handle table name change
     */
    async handleTableChange(e) {
        const tableName = e.target.value.trim();

        if (!tableName) {
            InputValidator.clearError('table-input');
            return;
        }

        try {
            InputValidator.clearError('table-input');
            const result = await api.setTable(tableName);
            this.state.table = result.table;
            await this.updateSQLPreview();
            Toast.success(`Table set to "${result.table}"`);
        } catch (error) {
            InputValidator.showError('table-input', error.message);
            Toast.error(error.message);
        }
    }

    /**
     * Handle add column
     */
    async handleAddColumn() {
        const column = this.elements.columnInput.value.trim();

        if (!column) {
            Toast.warning('Please enter a column name');
            return;
        }

        try {
            const result = await api.addColumn(column);
            this.state.columns = result.columns;
            this.elements.columnInput.value = '';
            ListRenderer.renderColumns(this.state.columns, (col) => this.handleRemoveColumn(col));
            await this.updateSQLPreview();
            Toast.success(`Column "${column}" added`);
        } catch (error) {
            Toast.error(error.message);
        }
    }

    /**
     * Handle remove column
     */
    async handleRemoveColumn(column) {
        try {
            const result = await api.removeColumn(column);
            this.state.columns = result.columns;
            ListRenderer.renderColumns(this.state.columns, (col) => this.handleRemoveColumn(col));
            await this.updateSQLPreview();
            Toast.success(`Column "${column}" removed`);
        } catch (error) {
            Toast.error(error.message);
        }
    }

    /**
     * Handle operator change (disable value for NULL operators)
     */
    handleOperatorChange() {
        const operator = this.elements.filterOperator.value;
        const isNullOperator = operator === 'IS NULL' || operator === 'IS NOT NULL';
        this.elements.filterValue.disabled = isNullOperator;

        if (isNullOperator) {
            this.elements.filterValue.value = '';
            this.elements.filterValue.placeholder = 'Not required';
        } else {
            this.elements.filterValue.placeholder = 'Value';
        }
    }

    /**
     * Handle add filter
     */
    async handleAddFilter() {
        const column = this.elements.filterColumn.value.trim();
        const operator = this.elements.filterOperator.value;
        let value = this.elements.filterValue.value.trim();

        if (!column) {
            Toast.warning('Please enter a column name');
            return;
        }

        // NULL operators don't need a value
        const isNullOperator = operator === 'IS NULL' || operator === 'IS NOT NULL';
        if (!isNullOperator && !value) {
            Toast.warning('Please enter a value');
            return;
        }

        // Convert value to null for NULL operators
        if (isNullOperator) {
            value = null;
        }

        try {
            const result = await api.addFilter(column, operator, value);
            this.state.filters = result.filters;
            
            // Clear inputs
            this.elements.filterColumn.value = '';
            this.elements.filterValue.value = '';
            
            ListRenderer.renderFilters(this.state.filters, (idx) => this.handleRemoveFilter(idx));
            await this.updateSQLPreview();
            Toast.success('Filter added');
        } catch (error) {
            Toast.error(error.message);
        }
    }

    /**
     * Handle remove filter
     */
    async handleRemoveFilter(index) {
        try {
            const result = await api.removeFilter(index);
            this.state.filters = result.filters;
            ListRenderer.renderFilters(this.state.filters, (idx) => this.handleRemoveFilter(idx));
            await this.updateSQLPreview();
            Toast.success('Filter removed');
        } catch (error) {
            Toast.error(error.message);
        }
    }

    /**
     * Handle clear query
     */
    async handleClearQuery() {
        if (!confirm('Clear entire query?')) {
            return;
        }

        try {
            await api.clearQuery();
            this.state.table = null;
            this.state.columns = [];
            this.state.filters = [];
            this.state.sql = '';

            // Clear UI
            this.elements.tableInput.value = '';
            this.elements.columnInput.value = '';
            this.elements.filterColumn.value = '';
            this.elements.filterValue.value = '';
            InputValidator.clearAllErrors();

            this.renderState();
            await this.updateSQLPreview();
            Toast.success('Query cleared');
        } catch (error) {
            Toast.error(error.message);
        }
    }

    /**
     * Handle copy SQL
     */
    async handleCopy() {
        if (!this.state.sql || this.state.sql.startsWith('--')) {
            Toast.warning('No SQL to copy');
            return;
        }

        await Clipboard.copy(this.state.sql);
    }

    /**
     * Handle download SQL
     */
    handleDownload() {
        if (!this.state.sql || this.state.sql.startsWith('--')) {
            Toast.warning('No SQL to download');
            return;
        }

        const filename = this.state.table ? `${this.state.table}.sql` : 'query.sql';
        FileDownload.download(this.state.sql, filename);
    }

    /**
     * Update SQL preview
     */
    async updateSQLPreview() {
        try {
            const result = await api.getSQL();
            this.state.sql = result.formatted || result.sql;
            await SQLDisplay.update(this.state.sql);
        } catch (error) {
            console.error('Error updating SQL preview:', error);
            await SQLDisplay.update('-- Error generating SQL');
        }
    }

    /**
     * Render current state to UI
     */
    renderState() {
        // Update dialect selector
        this.elements.dialectSelect.value = this.state.dialect;

        // Update table input
        this.elements.tableInput.value = this.state.table || '';

        // Render columns
        ListRenderer.renderColumns(this.state.columns, (col) => this.handleRemoveColumn(col));

        // Render filters
        ListRenderer.renderFilters(this.state.filters, (idx) => this.handleRemoveFilter(idx));

        // Update filter value input state
        this.handleOperatorChange();
    }
}

// Initialize app when DOM is ready
document.addEventListener('DOMContentLoaded', () => {
    window.app = new SQLTransApp();
});
