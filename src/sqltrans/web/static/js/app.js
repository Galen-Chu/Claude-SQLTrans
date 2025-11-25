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
        this.storage = new QueryStorage();
        this.autoSaveTimer = null;
        this.isSidebarOpen = false;
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
            // History elements
            historyToggleBtn: document.getElementById('history-toggle-btn'),
            historySidebar: document.getElementById('history-sidebar'),
            closeSidebarBtn: document.getElementById('close-sidebar-btn'),
            saveQueryBtn: document.getElementById('save-query-btn'),
            exportHistoryBtn: document.getElementById('export-history-btn'),
            importHistoryBtn: document.getElementById('import-history-btn'),
            historySearch: document.getElementById('history-search'),
            historyList: document.getElementById('history-list'),
            historyEmpty: document.getElementById('history-empty'),
            historyCount: document.getElementById('history-count'),
            historySize: document.getElementById('history-size'),
            saveQueryModal: document.getElementById('save-query-modal'),
            queryNameInput: document.getElementById('query-name-input'),
            importFileInput: document.getElementById('import-file-input'),
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

        // History sidebar
        this.elements.historyToggleBtn.addEventListener('click', () => this.toggleHistorySidebar());
        this.elements.closeSidebarBtn.addEventListener('click', () => this.toggleHistorySidebar());

        // History actions
        this.elements.saveQueryBtn.addEventListener('click', () => this.showSaveQueryModal());
        this.elements.exportHistoryBtn.addEventListener('click', () => this.handleExportHistory());
        this.elements.importHistoryBtn.addEventListener('click', () => this.handleImportHistoryClick());
        this.elements.importFileInput.addEventListener('change', (e) => this.handleImportHistory(e));

        // History search
        this.elements.historySearch.addEventListener('input', (e) => this.handleHistorySearch(e.target.value));

        // Save query modal
        const modalCloseButtons = this.elements.saveQueryModal.querySelectorAll('.modal-close, [data-action="cancel"]');
        modalCloseButtons.forEach(btn => {
            btn.addEventListener('click', () => this.closeSaveQueryModal());
        });

        const modalSaveButton = this.elements.saveQueryModal.querySelector('[data-action="save"]');
        modalSaveButton.addEventListener('click', () => this.handleSaveQuery());

        this.elements.queryNameInput.addEventListener('keypress', (e) => {
            if (e.key === 'Enter') {
                e.preventDefault();
                this.handleSaveQuery();
            }
        });

        // Close modal when clicking outside
        this.elements.saveQueryModal.addEventListener('click', (e) => {
            if (e.target === this.elements.saveQueryModal) {
                this.closeSaveQueryModal();
            }
        });

        // Keyboard shortcuts
        document.addEventListener('keydown', (e) => {
            // Ctrl+H to toggle history
            if ((e.ctrlKey || e.metaKey) && e.key === 'h') {
                e.preventDefault();
                this.toggleHistorySidebar();
            }
            // Escape to close sidebar and modals
            if (e.key === 'Escape') {
                if (this.isSidebarOpen) {
                    this.toggleHistorySidebar();
                }
                if (!this.elements.saveQueryModal.classList.contains('hidden')) {
                    this.closeSaveQueryModal();
                }
            }
        });
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
            this.renderHistory();
            this.updateHistoryStats();
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
            this.scheduleAutoSave();
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
            this.scheduleAutoSave();
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
            this.scheduleAutoSave();
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
            this.scheduleAutoSave();
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
            this.scheduleAutoSave();
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

    // ==================== History Management Methods ====================

    /**
     * Schedule auto-save with debouncing (2 seconds)
     */
    scheduleAutoSave() {
        // Skip if query is empty
        if (!this.state.table && this.state.columns.length === 0 && this.state.filters.length === 0) {
            return;
        }

        // Clear existing timer
        if (this.autoSaveTimer) {
            clearTimeout(this.autoSaveTimer);
        }

        // Schedule new auto-save
        this.autoSaveTimer = setTimeout(() => {
            try {
                const name = `[Auto-save] ${this.storage._generateDefaultName(this.state)}`;
                this.storage.saveQuery(this.state, name);
                this.updateHistoryStats();
                console.log('Auto-saved query');
            } catch (error) {
                console.error('Auto-save failed:', error);
            }
        }, 2000);
    }

    /**
     * Toggle history sidebar
     */
    toggleHistorySidebar() {
        this.isSidebarOpen = !this.isSidebarOpen;
        this.elements.historySidebar.classList.toggle('collapsed');

        if (this.isSidebarOpen) {
            this.renderHistory();
            this.updateHistoryStats();
        }
    }

    /**
     * Show save query modal
     */
    showSaveQueryModal() {
        // Check if there's a query to save
        if (!this.state.table && this.state.columns.length === 0) {
            Toast.warning('Build a query first before saving');
            return;
        }

        // Generate default name
        const defaultName = this.storage._generateDefaultName(this.state);
        this.elements.queryNameInput.value = defaultName;
        this.elements.queryNameInput.select();

        this.elements.saveQueryModal.classList.remove('hidden');
        this.elements.saveQueryModal.classList.add('show');
        this.elements.queryNameInput.focus();
    }

    /**
     * Close save query modal
     */
    closeSaveQueryModal() {
        this.elements.saveQueryModal.classList.remove('show');
        this.elements.saveQueryModal.classList.add('hidden');
        this.elements.queryNameInput.value = '';
    }

    /**
     * Handle save query
     */
    handleSaveQuery() {
        const name = this.elements.queryNameInput.value.trim();

        if (!name) {
            Toast.warning('Please enter a name for the query');
            return;
        }

        try {
            this.storage.saveQuery(this.state, name);
            this.closeSaveQueryModal();
            this.renderHistory();
            this.updateHistoryStats();
            Toast.success(`Query "${name}" saved`);
        } catch (error) {
            Toast.error(error.message);
        }
    }

    /**
     * Handle load query
     */
    async handleLoadQuery(id) {
        try {
            const query = this.storage.loadQuery(id);

            if (!query) {
                Toast.error('Query not found');
                return;
            }

            // Load query state
            const queryState = query.queryState;

            // Update backend
            await api.clearQuery();

            if (queryState.table) {
                await api.setTable(queryState.table);
            }

            if (queryState.dialect) {
                await api.setDialect(queryState.dialect);
            }

            for (const column of queryState.columns) {
                await api.addColumn(column);
            }

            for (const filter of queryState.filters) {
                await api.addFilter(filter.column, filter.operator, filter.value);
            }

            // Update local state
            this.state = queryState;
            this.renderState();
            await this.updateSQLPreview();
            this.renderHistory();
            this.updateHistoryStats();

            Toast.success(`Loaded "${query.name}"`);
        } catch (error) {
            Toast.error(`Failed to load query: ${error.message}`);
            console.error(error);
        }
    }

    /**
     * Handle delete query
     */
    handleDeleteQuery(id) {
        const query = this.storage.loadQuery(id);

        if (!query) {
            return;
        }

        if (!confirm(`Delete query "${query.name}"?`)) {
            return;
        }

        try {
            this.storage.deleteQuery(id);
            this.renderHistory();
            this.updateHistoryStats();
            Toast.success('Query deleted');
        } catch (error) {
            Toast.error(error.message);
        }
    }

    /**
     * Handle history search
     */
    handleHistorySearch(searchTerm) {
        this.renderHistory(searchTerm);
    }

    /**
     * Handle export history
     */
    handleExportHistory() {
        try {
            const jsonData = this.storage.exportHistory();
            const filename = `sqltrans_history_${new Date().toISOString().slice(0, 10)}.json`;

            const blob = new Blob([jsonData], { type: 'application/json' });
            const url = URL.createObjectURL(blob);
            const a = document.createElement('a');
            a.href = url;
            a.download = filename;
            a.click();
            URL.revokeObjectURL(url);

            Toast.success('History exported');
        } catch (error) {
            Toast.error(`Export failed: ${error.message}`);
        }
    }

    /**
     * Handle import history click (trigger file input)
     */
    handleImportHistoryClick() {
        this.elements.importFileInput.click();
    }

    /**
     * Handle import history from file
     */
    async handleImportHistory(event) {
        const file = event.target.files[0];

        if (!file) {
            return;
        }

        try {
            const text = await file.text();
            const result = this.storage.importHistory(text, true); // merge = true

            this.renderHistory();
            this.updateHistoryStats();

            Toast.success(`Imported ${result.added} queries (${result.skipped} duplicates skipped)`);
        } catch (error) {
            Toast.error(`Import failed: ${error.message}`);
        } finally {
            // Reset file input
            this.elements.importFileInput.value = '';
        }
    }

    /**
     * Render history list
     */
    renderHistory(searchTerm = '') {
        const queries = this.storage.listQueries(searchTerm);

        // Show/hide empty state
        if (queries.length === 0) {
            this.elements.historyList.style.display = 'none';
            this.elements.historyEmpty.style.display = 'flex';
            return;
        }

        this.elements.historyList.style.display = 'block';
        this.elements.historyEmpty.style.display = 'none';

        // Render query items
        this.elements.historyList.innerHTML = queries.map(query => `
            <li class="history-item" data-id="${query.id}">
                <div class="history-item-content" data-action="load">
                    <div class="history-item-header">
                        <span class="history-item-name">${this.escapeHtml(query.name)}</span>
                        <span class="history-item-badge">${query.queryState.dialect}</span>
                    </div>
                    <div class="history-item-details">
                        ${query.queryState.table ? `<span>Table: ${this.escapeHtml(query.queryState.table)}</span>` : ''}
                        ${query.queryState.columns.length > 0 ? `<span>${query.queryState.columns.length} columns</span>` : ''}
                        ${query.queryState.filters.length > 0 ? `<span>${query.queryState.filters.length} filters</span>` : ''}
                    </div>
                    <div class="history-item-meta">
                        <span class="history-item-date">${this.formatDate(query.metadata.lastUsed)}</span>
                        <span class="history-item-uses">Used ${query.metadata.useCount}x</span>
                    </div>
                </div>
                <button class="history-item-delete" data-action="delete" title="Delete query">
                    <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                        <path d="M3 6h18M8 6V4c0-1 1-2 2-2h4c1 0 2 1 2 2v2m3 0v14c0 1-1 2-2 2H7c-1 0-2-1-2-2V6h14z"/>
                    </svg>
                </button>
            </li>
        `).join('');

        // Attach click handlers
        this.elements.historyList.querySelectorAll('.history-item').forEach(item => {
            const id = item.dataset.id;

            item.querySelector('[data-action="load"]').addEventListener('click', () => {
                this.handleLoadQuery(id);
            });

            item.querySelector('[data-action="delete"]').addEventListener('click', (e) => {
                e.stopPropagation();
                this.handleDeleteQuery(id);
            });
        });
    }

    /**
     * Update history statistics
     */
    updateHistoryStats() {
        const stats = this.storage.getStats();
        this.elements.historyCount.textContent = `${stats.count} ${stats.count === 1 ? 'query' : 'queries'}`;
        this.elements.historySize.textContent = `${stats.sizeKB} KB`;
    }

    /**
     * Escape HTML to prevent XSS
     */
    escapeHtml(text) {
        const div = document.createElement('div');
        div.textContent = text;
        return div.innerHTML;
    }

    /**
     * Format date for display
     */
    formatDate(isoString) {
        const date = new Date(isoString);
        const now = new Date();
        const diffMs = now - date;
        const diffMins = Math.floor(diffMs / 60000);
        const diffHours = Math.floor(diffMs / 3600000);
        const diffDays = Math.floor(diffMs / 86400000);

        if (diffMins < 1) return 'Just now';
        if (diffMins < 60) return `${diffMins}m ago`;
        if (diffHours < 24) return `${diffHours}h ago`;
        if (diffDays < 7) return `${diffDays}d ago`;

        return date.toLocaleDateString();
    }

    // ==================== End History Methods ====================

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
