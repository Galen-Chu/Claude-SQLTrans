/**
 * API Client for the SQLTrans v2 backend.
 * Wraps the Translate / Ask / Run / Schema + connection + feedback endpoints.
 */
class APIClient {
    constructor(baseURL = "/api") {
        this.baseURL = baseURL;
    }

    async request(endpoint, options = {}) {
        const url = `${this.baseURL}${endpoint}`;
        const config = { headers: { "Content-Type": "application/json", ...options.headers }, ...options };
        const response = await fetch(url, config);
        const data = await response.json().catch(() => ({}));
        if (!response.ok) {
            throw new Error(data.detail || data.error || `Request failed (${response.status})`);
        }
        return data;
    }

    listConnections() {
        return this.request("/connections");
    }

    listDialects() {
        return this.request("/transpile/dialects").then((d) => d.dialects);
    }

    transpile({ sql, read, write, pretty = true }) {
        return this.request("/transpile", {
            method: "POST",
            body: JSON.stringify({ sql, read: read || null, write: write || null, pretty }),
        });
    }

    nl2sql({ prompt, dialect, connection_name, model, transpile_to }) {
        return this.request("/nl2sql", {
            method: "POST",
            body: JSON.stringify({
                prompt,
                dialect: dialect || null,
                connection_name: connection_name || null,
                model: model || null,
                transpile_to: transpile_to || null,
            }),
        });
    }

    feedback(payload) {
        return this.request("/nl2sql/feedback", {
            method: "POST",
            body: JSON.stringify(payload),
        });
    }

    schema({ connection_name, connection, schema }) {
        const params = new URLSearchParams();
        if (connection_name) params.set("connection_name", connection_name);
        if (connection) params.set("connection", connection);
        if (schema) params.set("schema", schema);
        return this.request(`/schema?${params.toString()}`);
    }

    execute({ sql, connection_name, connection, dialect, row_limit }) {
        return this.request("/query/execute", {
            method: "POST",
            body: JSON.stringify({
                sql,
                connection_name: connection_name || null,
                connection: connection || null,
                dialect: dialect || null,
                row_limit: row_limit || null,
            }),
        });
    }
}

window.api = new APIClient();
