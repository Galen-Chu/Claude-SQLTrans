/**
 * Query Storage Manager
 *
 * Manages query persistence using browser localStorage.
 * Provides save, load, delete, export, and import functionality.
 */

class QueryStorage {
    constructor() {
        this.storageKey = 'sqltrans_query_history';
        this.maxQueries = 50;
    }

    /**
     * Save a query to history
     * @param {Object} queryState - Current query state
     * @param {string} name - User-provided name for the query
     * @returns {string} - ID of saved query
     */
    saveQuery(queryState, name) {
        try {
            const history = this._getStorage();

            // Create query record
            const query = {
                id: this._generateId(),
                name: name || this._generateDefaultName(queryState),
                queryState: { ...queryState },
                metadata: {
                    createdAt: new Date().toISOString(),
                    lastUsed: new Date().toISOString(),
                    useCount: 1
                }
            };

            // Add to beginning of array
            history.unshift(query);

            // Prune if needed
            this._pruneOldQueries(history);

            // Save to localStorage
            this._setStorage(history);

            return query.id;
        } catch (error) {
            console.error('Failed to save query:', error);
            throw new Error('Failed to save query. Storage may be full.');
        }
    }

    /**
     * Load a query by ID
     * @param {string} id - Query ID
     * @returns {Object|null} - Query object or null if not found
     */
    loadQuery(id) {
        try {
            const history = this._getStorage();
            const query = history.find(q => q.id === id);

            if (query) {
                // Update metadata
                query.metadata.lastUsed = new Date().toISOString();
                query.metadata.useCount++;
                this._setStorage(history);
            }

            return query;
        } catch (error) {
            console.error('Failed to load query:', error);
            return null;
        }
    }

    /**
     * Get all saved queries
     * @param {string} searchTerm - Optional search term to filter queries
     * @returns {Array} - Array of query objects
     */
    listQueries(searchTerm = '') {
        try {
            const history = this._getStorage();

            if (!searchTerm) {
                return history;
            }

            // Filter by name or table name
            const term = searchTerm.toLowerCase();
            return history.filter(q =>
                q.name.toLowerCase().includes(term) ||
                (q.queryState.table && q.queryState.table.toLowerCase().includes(term))
            );
        } catch (error) {
            console.error('Failed to list queries:', error);
            return [];
        }
    }

    /**
     * Delete a query by ID
     * @param {string} id - Query ID
     * @returns {boolean} - Success status
     */
    deleteQuery(id) {
        try {
            const history = this._getStorage();
            const index = history.findIndex(q => q.id === id);

            if (index === -1) {
                return false;
            }

            history.splice(index, 1);
            this._setStorage(history);
            return true;
        } catch (error) {
            console.error('Failed to delete query:', error);
            return false;
        }
    }

    /**
     * Clear all query history
     * @returns {boolean} - Success status
     */
    clearAll() {
        try {
            this._setStorage([]);
            return true;
        } catch (error) {
            console.error('Failed to clear history:', error);
            return false;
        }
    }

    /**
     * Export query history as JSON file
     * @returns {string} - JSON string of history
     */
    exportHistory() {
        try {
            const history = this._getStorage();
            const exportData = {
                version: '1.0',
                exportedAt: new Date().toISOString(),
                queries: history
            };

            return JSON.stringify(exportData, null, 2);
        } catch (error) {
            console.error('Failed to export history:', error);
            throw new Error('Failed to export history');
        }
    }

    /**
     * Import query history from JSON
     * @param {string} jsonData - JSON string to import
     * @param {boolean} merge - Whether to merge with existing history
     * @returns {Object} - Import result {success, added, skipped}
     */
    importHistory(jsonData, merge = true) {
        try {
            // Parse and validate
            const importData = JSON.parse(jsonData);

            if (!importData.queries || !Array.isArray(importData.queries)) {
                throw new Error('Invalid import format');
            }

            // Validate each query
            const validQueries = importData.queries.filter(q =>
                this._validateQuery(q)
            );

            if (validQueries.length === 0) {
                throw new Error('No valid queries found in import data');
            }

            let history = merge ? this._getStorage() : [];
            let added = 0;
            let skipped = 0;

            // Add queries, avoiding duplicates
            for (const query of validQueries) {
                // Check for duplicate based on content
                const isDuplicate = history.some(existing =>
                    this._areQueriesEqual(existing.queryState, query.queryState)
                );

                if (!isDuplicate) {
                    // Generate new ID to avoid conflicts
                    query.id = this._generateId();
                    history.push(query);
                    added++;
                } else {
                    skipped++;
                }
            }

            // Prune if needed
            this._pruneOldQueries(history);

            // Save
            this._setStorage(history);

            return { success: true, added, skipped };
        } catch (error) {
            console.error('Failed to import history:', error);
            throw new Error(`Failed to import history: ${error.message}`);
        }
    }

    /**
     * Get storage statistics
     * @returns {Object} - Storage stats
     */
    getStats() {
        try {
            const history = this._getStorage();
            const storageData = JSON.stringify(history);
            const sizeInBytes = new Blob([storageData]).size;
            const sizeInKB = (sizeInBytes / 1024).toFixed(2);

            return {
                count: history.length,
                sizeKB: parseFloat(sizeInKB),
                maxQueries: this.maxQueries,
                percentFull: ((history.length / this.maxQueries) * 100).toFixed(1)
            };
        } catch (error) {
            console.error('Failed to get stats:', error);
            return { count: 0, sizeKB: 0, maxQueries: this.maxQueries, percentFull: 0 };
        }
    }

    // ==================== Private Helper Methods ====================

    /**
     * Generate unique ID for query
     * @returns {string} - Unique ID
     */
    _generateId() {
        return `query_${Date.now()}_${Math.random().toString(36).substr(2, 9)}`;
    }

    /**
     * Generate default name for query
     * @param {Object} queryState - Query state
     * @returns {string} - Default name
     */
    _generateDefaultName(queryState) {
        const table = queryState.table || 'untitled';
        const dialect = queryState.dialect || 'generic';
        const timestamp = new Date().toLocaleString();
        return `${table} (${dialect}) - ${timestamp}`;
    }

    /**
     * Prune old queries when limit exceeded
     * @param {Array} history - Query history array
     */
    _pruneOldQueries(history) {
        if (history.length > this.maxQueries) {
            // Sort by lastUsed (oldest first)
            history.sort((a, b) =>
                new Date(a.metadata.lastUsed) - new Date(b.metadata.lastUsed)
            );

            // Remove oldest queries
            const toRemove = history.length - this.maxQueries;
            history.splice(0, toRemove);
        }
    }

    /**
     * Get storage data from localStorage
     * @returns {Array} - Query history array
     */
    _getStorage() {
        try {
            const data = localStorage.getItem(this.storageKey);
            return data ? JSON.parse(data) : [];
        } catch (error) {
            console.error('Failed to read localStorage:', error);
            return [];
        }
    }

    /**
     * Set storage data to localStorage
     * @param {Array} data - Query history array
     */
    _setStorage(data) {
        try {
            localStorage.setItem(this.storageKey, JSON.stringify(data));
        } catch (error) {
            if (error.name === 'QuotaExceededError') {
                throw new Error('Storage quota exceeded. Try clearing old queries.');
            }
            throw error;
        }
    }

    /**
     * Validate query object structure
     * @param {Object} query - Query object to validate
     * @returns {boolean} - Whether query is valid
     */
    _validateQuery(query) {
        return query &&
               typeof query.name === 'string' &&
               query.queryState &&
               typeof query.queryState === 'object' &&
               query.metadata &&
               typeof query.metadata === 'object';
    }

    /**
     * Check if two queries are equal (same content)
     * @param {Object} q1 - First query state
     * @param {Object} q2 - Second query state
     * @returns {boolean} - Whether queries are equal
     */
    _areQueriesEqual(q1, q2) {
        return JSON.stringify(q1) === JSON.stringify(q2);
    }
}

// Export for use in other modules
if (typeof window !== 'undefined') {
    window.QueryStorage = QueryStorage;
}
