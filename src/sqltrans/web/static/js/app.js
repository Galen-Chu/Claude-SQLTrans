/**
 * SQLTrans web app — wires the Translate / Ask / Run / Schema views to the API.
 */
(function () {
    "use strict";

    const el = (id) => document.getElementById(id);

    function switchView(name) {
        document.querySelectorAll(".view").forEach((v) => v.classList.remove("active"));
        const target = document.getElementById(`view-${name}`);
        if (target) target.classList.add("active");
        document.querySelectorAll("#tabs button").forEach((b) => {
            b.classList.toggle("active", b.dataset.view === name);
        });
    }

    function fillSelect(select, values) {
        values.forEach((v) => {
            const opt = document.createElement("option");
            opt.value = v;
            opt.textContent = v;
            select.appendChild(opt);
        });
    }

    function connParams(prefix) {
        const name = el(`${prefix}-conn`).value;
        if (name) return { connection_name: name };
        const url = el(`${prefix}-url`).value.trim();
        if (url) return { connection: url };
        return null;
    }

    async function withButton(button, fn) {
        button.disabled = true;
        try {
            await fn();
        } finally {
            button.disabled = false;
        }
    }

    // ---- Translate ----
    async function doTranslate(button) {
        const sql = el("translate-input").value.trim();
        if (!sql) return UI.toast("Enter source SQL", "error");
        await withButton(button, async () => {
            try {
                const r = await api.transpile({
                    sql,
                    read: el("translate-read").value,
                    write: el("translate-write").value,
                });
                UI.renderSql(el("translate-output"), r.sql);
            } catch (e) {
                UI.toast(e.message, "error");
            }
        });
    }

    // ---- Ask (NL→SQL) ----
    let lastAsk = null;

    async function doAsk(button) {
        const prompt = el("ask-prompt").value.trim();
        if (!prompt) return UI.toast("Enter a request", "error");
        await withButton(button, async () => {
            try {
                const r = await api.nl2sql({
                    prompt,
                    dialect: el("ask-dialect").value,
                    connection_name: el("ask-conn").value || null,
                });
                el("ask-status").innerHTML = r.sql
                    ? `<span class="badge ${r.validated ? "ok" : "warn"}">${r.validated ? "validated" : "not validated"}</span>`
                    : "";
                UI.renderSql(el("ask-output"), r.sql || "-- no SQL generated");
                el("ask-warnings").innerHTML = (r.warnings || [])
                    .map((w) => `<div>${escapeHtml(w)}</div>`)
                    .join("");
                if (r.sql) {
                    lastAsk = { prompt, sql: r.sql, validated: r.validated, dialect: r.dialect };
                    el("ask-feedback").style.display = "flex";
                } else {
                    lastAsk = null;
                    el("ask-feedback").style.display = "none";
                }
            } catch (e) {
                UI.toast(e.message, "error");
            }
        });
    }

    async function sendFeedback(accepted) {
        if (!lastAsk) return;
        try {
            await api.feedback({
                prompt: lastAsk.prompt,
                sql: lastAsk.sql,
                accepted,
                dialect: lastAsk.dialect,
                validated: lastAsk.validated,
            });
            UI.toast(accepted ? "Thanks — recorded as helpful" : "Thanks — recorded as not helpful", "success");
        } catch (e) {
            UI.toast(e.message, "error");
        }
    }

    // ---- Run ----
    async function doRun(button) {
        const params = connParams("run");
        if (!params) return UI.toast("Select a connection or enter a URL", "error");
        const sql = el("run-sql").value.trim();
        if (!sql) return UI.toast("Enter SQL", "error");
        const row_limit = parseInt(el("run-limit").value, 10) || 1000;
        await withButton(button, async () => {
            try {
                const r = await api.execute({ sql, ...params, row_limit });
                UI.renderTable(el("run-results"), r.columns, r.rows);
                el("run-meta").textContent = `${r.row_count} row(s)${r.truncated ? " (truncated)" : ""}`;
            } catch (e) {
                UI.toast(e.message, "error");
            }
        });
    }

    // ---- Schema ----
    async function doSchema(button) {
        const params = connParams("schema");
        if (!params) return UI.toast("Select a connection or enter a URL", "error");
        const schema = el("schema-name").value.trim() || null;
        await withButton(button, async () => {
            try {
                const r = await api.schema({ ...params, schema });
                UI.renderSchema(el("schema-tree"), r.tables);
            } catch (e) {
                UI.toast(e.message, "error");
            }
        });
    }

    async function init() {
        // Theme
        window.theme = new ThemeManager();
        window.theme.init();
        el("theme-toggle-btn").addEventListener("click", () => window.theme.toggle());

        // Tabs
        document.querySelectorAll("#tabs button").forEach((b) => {
            b.addEventListener("click", () => switchView(b.dataset.view));
        });

        // Dialects
        try {
            const dialects = await api.listDialects();
            fillSelect(el("translate-read"), dialects);
            fillSelect(el("translate-write"), dialects);
            fillSelect(el("ask-dialect"), dialects);
        } catch (e) {
            UI.toast("Could not load dialects", "error");
        }

        // Connections
        try {
            const data = await api.listConnections();
            const names = (data.connections || []).map((c) => c.name);
            el("conn-badge").textContent = `connections: ${names.length ? names.join(", ") : "none"}`;
            fillSelect(el("ask-conn"), names);
            fillSelect(el("run-conn"), names);
            fillSelect(el("schema-conn"), names);
        } catch (e) {
            UI.toast("Could not load connections", "error");
        }

        // Buttons
        el("translate-btn").addEventListener("click", () => doTranslate(el("translate-btn")));
        el("translate-copy").addEventListener("click", () => {
            navigator.clipboard.writeText(el("translate-output").textContent).then(() =>
                UI.toast("Copied", "success")
            );
        });
        el("ask-btn").addEventListener("click", () => doAsk(el("ask-btn")));
        document.querySelectorAll("#ask-feedback button").forEach((b) => {
            b.addEventListener("click", () => sendFeedback(b.dataset.fb === "yes"));
        });
        el("run-btn").addEventListener("click", () => doRun(el("run-btn")));
        el("schema-btn").addEventListener("click", () => doSchema(el("schema-btn")));
    }

    window.App = { switchView };
    document.addEventListener("DOMContentLoaded", init);
})();
