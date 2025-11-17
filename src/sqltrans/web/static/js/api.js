/**
 * API Client for SQLTrans Backend
 * Handles all HTTP requests to the FastAPI backend
 */

class APIClient {
    constructor(baseURL = '/api') {
        this.baseURL = baseURL;
    }

    /**
     * Generic request handler
     * @param {string} endpoint - API endpoint path
     * @param {object} options - Fetch options
     * @returns {Promise<any>} Response data
     */
    async request(endpoint, options = {}) {
        const url = `${this.baseURL}${endpoint}`;
        const config = {
            headers: {
                'Content-Type': 'application/json',
                ...options.headers,
            },
            ...options,
        };

        try {
            const response = await fetch(url, config);
            const data = await response.json();

            if (!response.ok) {
                throw new Error(data.detail || data.error || 'Request failed');
            }

            return data;
        } catch (error) {
            console.error(`API Error [${endpoint}]:`, error);
            throw error;
        }
    }

    /**
     * Get current query state
     */
    async getQueryState() {
        return this.request('/query');
    }

    /**
     * Set table name
     */
    async setTable(name) {
        return this.request('/query/table', {
            method: 'POST',
            body: JSON.stringify({ name }),
        });
    }

    /**
     * Add a column
     */
    async addColumn(column) {
        return this.request('/query/columns/add', {
            method: 'POST',
            body: JSON.stringify({ column }),
        });
    }

    /**
     * Remove a column
     */
    async removeColumn(column) {
        return this.request(`/query/columns/${encodeURIComponent(column)}`, {
            method: 'DELETE',
        });
    }

    /**
     * Add a filter
     */
    async addFilter(column, operator, value) {
        return this.request('/query/filters/add', {
            method: 'POST',
            body: JSON.stringify({ column, operator, value }),
        });
    }

    /**
     * Remove a filter by index
     */
    async removeFilter(index) {
        return this.request(`/query/filters/${index}`, {
            method: 'DELETE',
        });
    }

    /**
     * Change SQL dialect
     */
    async setDialect(dialect) {
        return this.request('/query/dialect', {
            method: 'POST',
            body: JSON.stringify({ dialect }),
        });
    }

    /**
     * Clear entire query
     */
    async clearQuery() {
        return this.request('/query/clear', {
            method: 'POST',
        });
    }

    /**
     * Get generated SQL
     */
    async getSQL() {
        return this.request('/query/sql');
    }

    /**
     * Get available dialects
     */
    async getDialects() {
        return this.request('/dialects');
    }
}

// Create and export global API client instance
window.api = new APIClient();
