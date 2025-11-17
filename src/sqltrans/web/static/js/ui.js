/**
 * UI Utilities for SQLTrans Web GUI
 * Handles toast notifications, list rendering, and UI helpers
 */

/**
 * Toast notification system
 */
class Toast {
    static show(message, type = 'success', duration = 3000) {
        const container = document.getElementById('toast-container');
        const toast = document.createElement('div');
        toast.className = `toast toast-${type}`;

        toast.innerHTML = `
            <span class="toast-message">${this.escapeHTML(message)}</span>
            <button class="toast-close" onclick="this.parentElement.remove()">×</button>
        `;

        container.appendChild(toast);

        // Auto-remove after duration
        setTimeout(() => {
            if (toast.parentElement) {
                toast.style.animation = 'slideOut 0.3s ease';
                setTimeout(() => toast.remove(), 300);
            }
        }, duration);
    }

    static success(message) {
        this.show(message, 'success');
    }

    static error(message) {
        this.show(message, 'error', 5000);
    }

    static warning(message) {
        this.show(message, 'warning');
    }

    static escapeHTML(str) {
        const div = document.createElement('div');
        div.textContent = str;
        return div.innerHTML;
    }
}

/**
 * List renderer for columns and filters
 */
class ListRenderer {
    /**
     * Render column list
     */
    static renderColumns(columns, onRemove) {
        const list = document.getElementById('column-list');
        list.innerHTML = '';

        if (columns.length === 0) {
            list.innerHTML = '<li style="opacity: 0.6; font-style: italic;">No columns (SELECT * will be used)</li>';
            return;
        }

        columns.forEach(column => {
            const li = document.createElement('li');
            li.innerHTML = `
                <span class="item-content">${this.escapeHTML(column)}</span>
                <button class="item-remove" data-column="${this.escapeHTML(column)}" title="Remove column">×</button>
            `;

            li.querySelector('.item-remove').addEventListener('click', () => onRemove(column));
            list.appendChild(li);
        });
    }

    /**
     * Render filter list
     */
    static renderFilters(filters, onRemove) {
        const list = document.getElementById('filter-list');
        list.innerHTML = '';

        if (filters.length === 0) {
            list.innerHTML = '<li style="opacity: 0.6; font-style: italic;">No filters</li>';
            return;
        }

        filters.forEach((filter, index) => {
            const li = document.createElement('li');
            const valueDisplay = filter.value !== null && filter.value !== undefined
                ? ` '${this.escapeHTML(String(filter.value))}'`
                : '';

            li.innerHTML = `
                <span class="item-content">${this.escapeHTML(filter.column)} ${this.escapeHTML(filter.operator)}${valueDisplay}</span>
                <button class="item-remove" data-index="${index}" title="Remove filter">×</button>
            `;

            li.querySelector('.item-remove').addEventListener('click', () => onRemove(index));
            list.appendChild(li);
        });
    }

    static escapeHTML(str) {
        const div = document.createElement('div');
        div.textContent = str;
        return div.innerHTML;
    }
}

/**
 * Input validation and feedback
 */
class InputValidator {
    /**
     * Show validation error
     */
    static showError(inputId, message) {
        const input = document.getElementById(inputId);
        const errorSpan = document.getElementById(`${inputId}-error`);

        if (input) {
            input.style.borderColor = 'var(--error-color)';
        }

        if (errorSpan) {
            errorSpan.textContent = message;
            errorSpan.style.display = 'block';
        }
    }

    /**
     * Clear validation error
     */
    static clearError(inputId) {
        const input = document.getElementById(inputId);
        const errorSpan = document.getElementById(`${inputId}-error`);

        if (input) {
            input.style.borderColor = '';
        }

        if (errorSpan) {
            errorSpan.textContent = '';
            errorSpan.style.display = 'none';
        }
    }

    /**
     * Clear all errors
     */
    static clearAllErrors() {
        const errors = document.querySelectorAll('.validation-message');
        errors.forEach(error => {
            error.textContent = '';
            error.style.display = 'none';
        });

        const inputs = document.querySelectorAll('input[type="text"]');
        inputs.forEach(input => {
            input.style.borderColor = '';
        });
    }
}

/**
 * SQL display and syntax highlighting
 */
class SQLDisplay {
    /**
     * Update SQL preview with syntax highlighting
     */
    static async update(sql) {
        const preview = document.getElementById('sql-preview');
        
        if (!sql || sql.trim() === '') {
            preview.innerHTML = '<code class="language-sql">-- Build your query using the form on the left\n-- Start by entering a table name</code>';
            return;
        }

        // Update content with syntax highlighting
        preview.innerHTML = `<code class="language-sql">${this.escapeHTML(sql)}</code>`;
        
        // Apply Prism syntax highlighting if available
        if (window.Prism) {
            Prism.highlightElement(preview.querySelector('code'));
        }
    }

    static escapeHTML(str) {
        const div = document.createElement('div');
        div.textContent = str;
        return div.innerHTML;
    }
}

/**
 * Clipboard operations
 */
class Clipboard {
    /**
     * Copy text to clipboard
     */
    static async copy(text) {
        try {
            await navigator.clipboard.writeText(text);
            Toast.success('SQL copied to clipboard!');
            return true;
        } catch (error) {
            console.error('Clipboard copy failed:', error);
            Toast.error('Failed to copy to clipboard');
            return false;
        }
    }
}

/**
 * File download
 */
class FileDownload {
    /**
     * Download text as file
     */
    static download(text, filename = 'query.sql') {
        const blob = new Blob([text], { type: 'text/plain' });
        const url = URL.createObjectURL(blob);
        const a = document.createElement('a');
        a.href = url;
        a.download = filename;
        document.body.appendChild(a);
        a.click();
        document.body.removeChild(a);
        URL.revokeObjectURL(url);
        Toast.success(`Downloaded ${filename}`);
    }
}

// Export to window for global access
window.Toast = Toast;
window.ListRenderer = ListRenderer;
window.InputValidator = InputValidator;
window.SQLDisplay = SQLDisplay;
window.Clipboard = Clipboard;
window.FileDownload = FileDownload;
