/**
 * Theme Manager
 *
 * Handles theme switching between light and dark modes with OS preference detection.
 * Manages localStorage persistence and Prism.js theme swapping.
 */

class ThemeManager {
    constructor() {
        this.storageKey = 'sqltrans_theme';
        this.currentTheme = 'light';
        this.osPreferenceQuery = window.matchMedia('(prefers-color-scheme: dark)');
        
        // Bind methods to maintain 'this' context
        this.handleOSPreferenceChange = this.handleOSPreferenceChange.bind(this);
    }

    /**
     * Initialize theme system
     */
    init() {
        // Detect OS preference
        const osPreference = this.osPreferenceQuery.matches ? 'dark' : 'light';
        
        // Load saved preference from localStorage
        const savedTheme = this.loadTheme();
        
        // Determine initial theme (saved preference takes priority over OS preference)
        const initialTheme = savedTheme || osPreference;
        
        // Set initial theme
        this.setTheme(initialTheme, false); // Don't save during initialization
        
        // Listen for OS preference changes
        this.setupOSPreferenceListener();
        
        console.log(`ThemeManager initialized: ${initialTheme} (OS: ${osPreference})`);
    }

    /**
     * Set theme by name
     * @param {string} theme - Theme name ('light' or 'dark')
     * @param {boolean} save - Whether to save to localStorage (default: true)
     */
    setTheme(theme, save = true) {
        if (!['light', 'dark'].includes(theme)) {
            console.error(`Invalid theme: ${theme}. Must be 'light' or 'dark'`);
            return;
        }

        const previousTheme = this.currentTheme;
        this.currentTheme = theme;

        // Set data attribute on html element
        if (theme === 'dark') {
            document.documentElement.setAttribute('data-theme', 'dark');
        } else {
            document.documentElement.removeAttribute('data-theme');
        }

        // Update Prism.js syntax highlighting
        this.updatePrismTheme(theme);

        // Update theme toggle button icon
        this.updateToggleButton(theme);

        // Save to localStorage if requested
        if (save) {
            this.saveTheme(theme);
        }

        // Dispatch theme change event
        this.dispatchThemeChangeEvent(theme, previousTheme);

        console.log(`Theme changed to: ${theme}${save ? ' (saved)' : ' (not saved)'}`);
    }

    /**
     * Toggle between light and dark themes
     * @returns {string} - New theme name
     */
    toggle() {
        const newTheme = this.currentTheme === 'light' ? 'dark' : 'light';
        this.setTheme(newTheme);
        return newTheme;
    }

    /**
     * Update Prism.js CSS for syntax highlighting
     * @param {string} theme - Theme name
     */
    updatePrismTheme(theme) {
        const prismLightTheme = document.querySelector('link[href*="prism.css"]');
        const prismDarkTheme = document.querySelector('link[href*="prism-dark.css"]');

        if (theme === 'dark') {
            // Enable dark theme
            if (prismLightTheme && prismDarkTheme) {
                prismLightTheme.disabled = true;
                prismDarkTheme.disabled = false;
            }
        } else {
            // Enable light theme
            if (prismLightTheme && prismDarkTheme) {
                prismLightTheme.disabled = false;
                prismDarkTheme.disabled = true;
            }
        }
    }

    /**
     * Get current theme
     * @returns {string} - Current theme name
     */
    getCurrentTheme() {
        return this.currentTheme;
    }

    /**
     * Load theme from localStorage
     * @returns {string|null} - Saved theme name
     */
    loadTheme() {
        try {
            return localStorage.getItem(this.storageKey);
        } catch (error) {
            console.error('Failed to load theme from localStorage:', error);
            return null;
        }
    }

    /**
     * Save theme to localStorage
     * @param {string} theme - Theme name to save
     */
    saveTheme(theme) {
        try {
            localStorage.setItem(this.storageKey, theme);
        } catch (error) {
            console.error('Failed to save theme to localStorage:', error);
        }
    }

    /**
     * Clear theme preference from localStorage
     */
    clearTheme() {
        try {
            localStorage.removeItem(this.storageKey);
            console.log('Theme preference cleared');
        } catch (error) {
            console.error('Failed to clear theme from localStorage:', error);
        }
    }

    /**
     * Setup OS preference change listener
     */
    setupOSPreferenceListener() {
        try {
            this.osPreferenceQuery.addEventListener('change', this.handleOSPreferenceChange);
        } catch (error) {
            console.error('Failed to setup OS preference listener:', error);
        }
    }

    /**
     * Handle OS preference change
     * @param {MediaQueryListEvent} event - Media query change event
     */
    handleOSPreferenceChange(event) {
        const osPreference = event.matches ? 'dark' : 'light';
        console.log(`OS preference changed to: ${osPreference}`);

        // Only auto-switch if user hasn't explicitly set a preference
        if (!this.loadTheme()) {
            this.setTheme(osPreference, false);
        }
    }

    /**
     * Update theme toggle button icon
     * @param {string} theme - Current theme name
     */
    updateToggleButton(theme) {
        const toggleButton = document.getElementById('theme-toggle-btn');
        if (!toggleButton) {
            return;
        }

        const sunIcon = toggleButton.querySelector('.sun-icon');
        const moonIcon = toggleButton.querySelector('.moon-icon');

        if (theme === 'dark') {
            // Show sun icon (to switch to light)
            sunIcon.style.display = 'block';
            moonIcon.style.display = 'none';
        } else {
            // Show moon icon (to switch to dark)
            sunIcon.style.display = 'none';
            moonIcon.style.display = 'block';
        }
    }

    /**
     * Dispatch theme change event
     * @param {string} newTheme - New theme
     * @param {string} previousTheme - Previous theme
     */
    dispatchThemeChangeEvent(newTheme, previousTheme) {
        const event = new CustomEvent('themechange', {
            detail: { newTheme, previousTheme }
        });
        document.dispatchEvent(event);
    }

    /**
     * Check if dark mode is currently active
     * @returns {boolean} - Whether dark mode is active
     */
    isDarkMode() {
        return this.currentTheme === 'dark';
    }

    /**
     * Get CSS custom property value
     * @param {string} property - CSS custom property name (without --)
     * @returns {string} - Property value
     */
    getCSSVariable(property) {
        return getComputedStyle(document.documentElement)
            .getPropertyValue(`--${property}`)
            .trim();
    }

    /**
     * Apply theme to specific element (for dynamic components)
     * @param {HTMLElement} element - Element to apply theme to
     * @param {string} theme - Theme name
     */
    applyThemeToElement(element, theme) {
        element.setAttribute('data-theme', theme);
    }

    /**
     * Cleanup event listeners
     */
    destroy() {
        try {
            this.osPreferenceQuery.removeEventListener('change', this.handleOSPreferenceChange);
        } catch (error) {
            console.error('Failed to cleanup ThemeManager:', error);
        }
    }
}

// Export for use in other modules
if (typeof window !== 'undefined') {
    window.ThemeManager = ThemeManager;
}