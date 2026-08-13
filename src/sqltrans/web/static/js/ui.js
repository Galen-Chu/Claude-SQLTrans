/**
 * Small render + toast helpers for the SQLTrans UI.
 */
const UI = {
    /** Show a transient toast: type is "success" | "error". */
    toast(message, type = "success", timeout = 3500) {
        const container = document.getElementById("toast-container");
        const el = document.createElement("div");
        el.className = `toast ${type}`;
        el.textContent = message;
        container.appendChild(el);
        setTimeout(() => el.remove(), timeout);
    },

    /** Render a SQL string into a <code> element with Prism highlighting. */
    renderSql(codeEl, sql) {
        codeEl.textContent = sql;
        codeEl.className = "language-sql";
        if (window.Prism) {
            window.Prism.highlightElement(codeEl);
        }
    },

    /** Render a result set into a target element as a table. */
    renderTable(target, columns, rows) {
        if (!rows || rows.length === 0) {
            target.innerHTML = '<span class="muted">no rows</span>';
            return;
        }
        const head = columns.map((c) => `<th>${escapeHtml(c)}</th>`).join("");
        const body = rows
            .map((r) => `<tr>${r.map((v) => `<td>${escapeHtml(formatCell(v))}</td>`).join("")}</tr>`)
            .join("");
        target.innerHTML = `<table class="results"><thead><tr>${head}</tr></thead><tbody>${body}</tbody></table>`;
    },

    /** Render a schema (tables → columns) as a simple tree. */
    renderSchema(target, tables) {
        if (!tables || tables.length === 0) {
            target.innerHTML = '<span class="muted">no tables</span>';
            return;
        }
        target.innerHTML = tables
            .map(
                (t) =>
                    `<div><span class="table-name">${escapeHtml(t.name)}</span></div>` +
                    t.columns
                        .map(
                            (c) =>
                                `<div class="col">${escapeHtml(c.name)} (${escapeHtml(c.type)})` +
                                `${c.nullable ? "" : " NOT NULL"}</div>`
                        )
                        .join("")
            )
            .join("");
    },
};

function escapeHtml(value) {
    return String(value)
        .replace(/&/g, "&amp;")
        .replace(/</g, "&lt;")
        .replace(/>/g, "&gt;")
        .replace(/"/g, "&quot;");
}

function formatCell(value) {
    if (value === null || value === undefined) return "NULL";
    if (typeof value === "object") return JSON.stringify(value);
    return value;
}

window.UI = UI;
