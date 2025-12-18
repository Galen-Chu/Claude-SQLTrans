/**
 * Keyboard Shortcuts Manager
 *
 * Handles keyboard shortcuts for power users with help modal.
 * Supports both Ctrl (Windows/Linux) and Cmd (Mac) key combinations.
 * Provides visual feedback for shortcut execution.
 */

class KeyboardManager {
    constructor(app) {
        this.app = app;
        this.shortcuts = {
            // Query Operations
            'Ctrl+Enter': {
                action: 'copy',
                description: 'Copy SQL to clipboard',
                category: 'Query Operations'
            },
            'Ctrl+D': {
                action: 'download', 
                description: 'Download SQL file',
                category: 'Query Operations'
            },
            'Ctrl+K': {
                action: 'clear',
                description: 'Clear query',
                category: 'Query Operations'
            },
            
            // Navigation & UI
            'Ctrl+H': {
                action: 'toggle-history',
                description: 'Toggle query history',
                category: 'Navigation & UI'
            },
            'Ctrl+Shift+T': {
                action: 'toggle-theme',
                description: 'Toggle theme',
                category: 'Navigation & UI'
            },
            'Ctrl+/': {
                action: 'show-shortcuts',
                description: 'Show keyboard shortcuts',
                category: 'Navigation & UI'
            },
            'Escape': {
                action: 'close-modals',
                description: 'Close modals',
                category: 'Navigation & UI'
            }
        };

        // Bind methods to maintain 'this' context
        this.handleKeyPress = this.handleKeyPress.bind(this);
        this.showHelp = this.showHelp.bind(this);
        this.hideHelp = this.hideHelp.bind(this);
    }

    /**
     * Initialize keyboard shortcuts system
     */
    init() {
        document.addEventListener('keydown', this.handleKeyPress);
        console.log('KeyboardManager initialized with shortcuts:', Object.keys(this.shortcuts).length);
    }

    /**
     * Handle keyboard key press events
     * @param {KeyboardEvent} event - Key down event
     */
    handleKeyPress(event) {
        // Get the key combination string
        const keyCombo = this.getKeyCombo(event);

        // Find matching shortcut
        const shortcut = Object.keys(this.shortcuts).find(combo => 
            this.normalizeCombo(combo) === this.normalizeCombo(keyCombo)
        );

        if (!shortcut) {
            return; // No shortcut matches
        }

        const shortcutInfo = this.shortcuts[shortcut];

        // Prevent default browser behavior for our shortcuts
        event.preventDefault();
        event.stopPropagation();

        // Execute the shortcut action
        try {
            this.executeShortcut(shortcutInfo.action, keyCombo);
            console.log(`Keyboard shortcut triggered: ${keyCombo} -> ${shortcutInfo.action}`);
        } catch (error) {
            console.error(`Error executing shortcut ${keyCombo}:`, error);
            Toast.error(`Failed to execute shortcut: ${shortcutInfo.description}`);
        }
    }

    /**
     * Get key combination string from keyboard event
     * @param {KeyboardEvent} event - Keyboard event
     * @returns {string} - Key combination string (e.g., "Ctrl+Enter")
     */
    getKeyCombo(event) {
        const parts = [];

        // Modifier keys
        if (event.ctrlKey || event.metaKey) {
            // Use 'Ctrl' for both Ctrl and Cmd for consistency
            parts.push('Ctrl');
        }
        if (event.shiftKey) {
            parts.push('Shift');
        }
        if (event.altKey) {
            parts.push('Alt');
        }

        // Main key - handle special cases
        let mainKey = event.key;
        
        // Convert special keys to consistent names
        const specialKeys = {
            'Escape': 'Escape',
            'Enter': 'Enter',
            'Space': 'Space',
            'ArrowUp': 'ArrowUp',
            'ArrowDown': 'ArrowDown',
            'ArrowLeft': 'ArrowLeft',
            'ArrowRight': 'ArrowRight'
        };

        if (specialKeys[mainKey]) {
            mainKey = specialKeys[mainKey];
        } else if (mainKey.length === 1 && /[a-zA-Z0-9]/.test(mainKey)) {
            // Single letters/numbers should be uppercase for consistency
            mainKey = mainKey.toUpperCase();
        }

        parts.push(mainKey);

        return parts.join('+');
    }

    /**
     * Normalize key combination for comparison
     * @param {string} combo - Key combination string
     * @returns {string} - Normalized key combination
     */
    normalizeCombo(combo) {
        // Standardize the key combination string for comparison
        return combo
            .toUpperCase()
            .replace(/META\+/g, 'CTRL+') // Treat Meta as Ctrl for comparison
            .replace(/COMMAND\+/g, 'CTRL+') // Treat Cmd as Ctrl for comparison
            .trim();
    }

    /**
     * Execute a shortcut action
     * @param {string} action - Action name
     * @param {string} keyCombo - The actual key combination pressed
     */
    executeShortcut(action, keyCombo) {
        switch (action) {
            case 'copy':
                if (this.app.handleCopy) {
                    this.app.handleCopy();
                    Toast.success('SQL copied to clipboard');
                }
                break;

            case 'download':
                if (this.app.handleDownload) {
                    this.app.handleDownload();
                    Toast.success('SQL file downloaded');
                }
                break;

            case 'clear':
                if (this.app.handleClearQuery) {
                    this.app.handleClearQuery();
                    Toast.success('Query cleared');
                }
                break;

            case 'toggle-history':
                if (this.app.toggleHistorySidebar) {
                    this.app.toggleHistorySidebar();
                    Toast.info('History sidebar toggled');
                }
                break;

            case 'toggle-theme':
                if (this.app.themeManager) {
                    this.app.themeManager.toggle();
                    const newTheme = this.app.themeManager.getCurrentTheme();
                    Toast.success(`Theme switched to ${newTheme} mode`);
                }
                break;

            case 'show-shortcuts':
                this.showHelp();
                break;

            case 'close-modals':
                // Close any open modals and sidebars
                this.closeAllModals();
                break;

            default:
                console.warn(`Unknown shortcut action: ${action}`);
                break;
        }
    }

    /**
     * Show keyboard shortcuts help modal
     */
    showHelp() {
        // Create modal if it doesn't exist
        let modal = document.getElementById('shortcuts-modal');
        
        if (!modal) {
            modal = this.createHelpModal();
            document.body.appendChild(modal);
        }

        // Group shortcuts by category
        const shortcutsByCategory = this.groupShortcutsByCategory();
        
        // Populate modal with shortcuts
        this.populateHelpModal(modal, shortcutsByCategory);
        
        // Show modal
        modal.classList.remove('hidden');
        modal.classList.add('show');
        
        // Focus on modal for accessibility
        this.trapFocus(modal);

        console.log('Keyboard shortcuts help modal shown');
    }

    /**
     * Hide keyboard shortcuts help modal
     */
    hideHelp() {
        const modal = document.getElementById('shortcuts-modal');
        
        if (modal) {
            modal.classList.remove('show');
            modal.classList.add('hidden');
            this.removeFocusTrap(modal);
            
            console.log('Keyboard shortcuts help modal hidden');
        }
    }

    /**
     * Create the help modal DOM structure
     * @returns {HTMLElement} - Modal element
     */
    createHelpModal() {
        const modal = document.createElement('div');
        modal.id = 'shortcuts-modal';
        modal.className = 'modal';
        modal.setAttribute('role', 'dialog');
        modal.setAttribute('aria-labelledby', 'shortcuts-title');
        modal.setAttribute('aria-modal', 'true');

        modal.innerHTML = `
            <div class="modal-content">
                <div class="modal-header">
                    <h2 id="shortcuts-title">
                        <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                            <rect x="3" y="11" width="18" height="10" rx="2" ry="2"/>
                            <path d="M7 21v-6M13 21v-6M7 15l6-6M17 15l-6 6"/>
                            <circle cx="12" cy="8" r="4"/>
                        </svg>
                        Keyboard Shortcuts
                    </h2>
                    <button class="modal-close shortcuts-close" title="Close (Escape)">
                        <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                            <path d="M18 6L6 18M6 6l12 12"/>
                        </svg>
                    </button>
                </div>
                <div class="modal-body">
                    <div class="shortcuts-intro">
                        <p>Use these keyboard shortcuts to work faster and more efficiently. Shortcuts are available throughout the application.</p>
                        <p><strong>Platform Note:</strong> Use <kbd>Ctrl</kbd> on Windows/Linux or <kbd>Cmd</kbd> on Mac for shortcuts.</p>
                    </div>
                    <div class="shortcuts-content">
                        <!-- Shortcuts will be populated by populateHelpModal -->
                    </div>
                </div>
            </div>
        `;

        // Add event listeners
        modal.querySelector('.shortcuts-close').addEventListener('click', this.hideHelp);
        modal.addEventListener('click', (e) => {
            if (e.target === modal) {
                this.hideHelp();
            }
        });

        // Close with Escape key
        const escapeHandler = (e) => {
            if (e.key === 'Escape') {
                this.hideHelp();
                document.removeEventListener('keydown', escapeHandler);
            }
        };
        document.addEventListener('keydown', escapeHandler);

        return modal;
    }

    /**
     * Group shortcuts by category for display
     * @returns {Object} - Shortcuts grouped by category
     */
    groupShortcutsByCategory() {
        const grouped = {};
        
        Object.entries(this.shortcuts).forEach(([combo, info]) => {
            if (!grouped[info.category]) {
                grouped[info.category] = [];
            }
            grouped[info.category].push({ combo, ...info });
        });

        return grouped;
    }

    /**
     * Populate help modal with shortcuts
     * @param {HTMLElement} modal - Modal element
     * @param {Object} shortcutsByCategory - Grouped shortcuts
     */
    populateHelpModal(modal, shortcutsByCategory) {
        const contentContainer = modal.querySelector('.shortcuts-content');
        
        let html = '';
        
        Object.entries(shortcutsByCategory).forEach(([category, shortcuts]) => {
            html += `
                <div class="shortcuts-category">
                    <h3 class="category-title">${category}</h3>
                    <table class="shortcuts-table">
                        <thead>
                            <tr>
                                <th>Shortcut</th>
                                <th>Description</th>
                            </tr>
                        </thead>
                        <tbody>
                            ${shortcuts.map(shortcut => `
                                <tr>
                                    <td class="shortcut-combo">
                                        <kbd>${this.formatShortcutCombo(shortcut.combo)}</kbd>
                                    </td>
                                    <td class="shortcut-description">${shortcut.description}</td>
                                </tr>
                            `).join('')}
                        </tbody>
                    </table>
                </div>
            `;
        });

        contentContainer.innerHTML = html;
    }

    /**
     * Format shortcut combination for display
     * @param {string} combo - Key combination
     * @returns {string} - Formatted key combination
     */
    formatShortcutCombo(combo) {
        return combo
            .replace(/\+/g, ' + ')
            .replace(/CTRL/g, '<kbd>Ctrl</kbd>')
            .replace(/SHIFT/g, '<kbd>Shift</kbd>')
            .replace(/ALT/g, '<kbd>Alt</kbd>')
            .replace(/ENTER/g, '<kbd>Enter</kbd>')
            .replace(/ESCAPE/g, '<kbd>Esc</kbd>')
            .replace(/ARROWUP/g, '<kbd>↑</kbd>')
            .replace(/ARROWDOWN/g, '<kbd>↓</kbd>')
            .replace(/ARROWLEFT/g, '<kbd>←</kbd>')
            .replace(/ARROWRIGHT/g, '<kbd>→</kbd>')
            .replace(/SPACE/g, '<kbd>Space</kbd>');
    }

    /**
     * Close all open modals and sidebars
     */
    closeAllModals() {
        // Close any modal dialogs
        document.querySelectorAll('.modal.show').forEach(modal => {
            modal.classList.remove('show');
            modal.classList.add('hidden');
        });

        // Close any open sidebars
        const sidebar = document.getElementById('history-sidebar');
        if (sidebar && !sidebar.classList.contains('collapsed')) {
            if (this.app.toggleHistorySidebar) {
                this.app.toggleHistorySidebar();
                Toast.info('Closed sidebar and modals');
            }
        }
    }

    /**
     * Trap focus within modal for accessibility
     * @param {HTMLElement} modal - Modal element
     */
    trapFocus(modal) {
        const focusableElements = modal.querySelectorAll(
            'button, [href], input, select, textarea, [tabindex]:not([tabindex="-1"])'
        );
        
        const firstElement = focusableElements[0];
        const lastElement = focusableElements[focusableElements.length - 1];

        const focusHandler = (e) => {
            if (e.key === 'Tab') {
                if (e.shiftKey) {
                    if (document.activeElement === firstElement) {
                        lastElement.focus();
                        e.preventDefault();
                    }
                } else {
                    if (document.activeElement === lastElement) {
                        firstElement.focus();
                        e.preventDefault();
                    }
                }
            }
        };

        modal.addEventListener('keydown', focusHandler);
        firstElement.focus();
    }

    /**
     * Remove focus trap from modal
     * @param {HTMLElement} modal - Modal element
     */
    removeFocusTrap(modal) {
        modal.removeEventListener('keydown', this.focusHandler);
    }

    /**
     * Destroy keyboard manager and cleanup event listeners
     */
    destroy() {
        document.removeEventListener('keydown', this.handleKeyPress);
        console.log('KeyboardManager destroyed');
    }

    /**
     * Get all available shortcuts
     * @returns {Object} - Copy of shortcuts object
     */
    getShortcuts() {
        return { ...this.shortcuts };
    }

    /**
     * Add a new shortcut
     * @param {string} combo - Key combination
     * @param {Object} info - Shortcut information
     */
    addShortcut(combo, info) {
        this.shortcuts[combo] = info;
        console.log(`Added shortcut: ${combo} -> ${info.action}`);
    }

    /**
     * Remove a shortcut
     * @param {string} combo - Key combination to remove
     */
    removeShortcut(combo) {
        delete this.shortcuts[combo];
        console.log(`Removed shortcut: ${combo}`);
    }
}

// Export for use in other modules
if (typeof window !== 'undefined') {
    window.KeyboardManager = KeyboardManager;
}