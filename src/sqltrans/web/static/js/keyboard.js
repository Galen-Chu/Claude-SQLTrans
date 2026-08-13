/**
 * Minimal keyboard shortcuts for the v3 UI.
 *   Ctrl/Cmd + 1..4  → switch tabs (Translate / Ask / Run / Schema)
 *   Ctrl/Cmd + Shift + T → toggle theme
 */
(function () {
    "use strict";

    document.addEventListener("keydown", (event) => {
        const ctrl = event.ctrlKey || event.metaKey;
        if (!ctrl) return;

        // Tab navigation: Ctrl+1..4
        if (!event.shiftKey && !event.altKey && /^[1-4]$/.test(event.key)) {
            const views = ["translate", "ask", "run", "schema"];
            const target = views[Number(event.key) - 1];
            if (target && window.App && window.App.switchView) {
                event.preventDefault();
                window.App.switchView(target);
            }
            return;
        }

        // Theme toggle: Ctrl+Shift+T
        if (event.shiftKey && (event.key === "T" || event.key === "t")) {
            event.preventDefault();
            if (window.theme) window.theme.toggle();
        }
    });
})();
