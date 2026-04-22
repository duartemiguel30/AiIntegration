# Security Intelligence Aggregator

A Python backend service that fetches CVE vulnerability data from the NVD API, analyses each entry using a Gemini AI agent via an MCP server, and exposes the results through a REST API and web UI.

---

## How it works

On startup and every minute, an AI agent connects to the MCP server, discovers the available tools, and sends a prompt to Gemini. Gemini autonomously decides to call `fetchSecurityData` to retrieve CVEs from the NVD API, then calls `storeFinding` for each one. The results are stored in SQLite and exposed via a REST API.

The MCP server runs as a separate container — the agent has no hardcoded knowledge of what tools exist or how they work. It discovers everything at runtime via `list_tools()`.

---

## Stack

| Component | Technology |
|---|---|
| Backend | FastAPI |
| AI Agent | Google Gemini 2.5 Flash |
| Tool Protocol | MCP over SSE |
| Database | SQLite + SQLAlchemy |
| Scheduler | APScheduler |
| Container | Docker Compose |

---

## Setup

Create a `.env` file:
```env
GEMINI_API_KEY=key
```

```bash
docker compose up --build
```

---

## Endpoints

| | |
|---|---|
| `http://localhost:8000` | Web UI |
| `GET /api/findings/` | List findings — supports `?severity=` and `?topic=` |
| `GET /api/findings/{id}` | Get finding by CVE ID |
| `http://localhost:8001/sse` | MCP server |

---

## Security

| Control | Implementation |
|---|---|
| XSS | `escHtml()` on all UI output + Content-Security-Policy header |
| Clickjacking | `X-Frame-Options: DENY` |
| MIME sniffing | `X-Content-Type-Options: nosniff` |
| Rate limiting | 60 req/min per IP via slowapi |
| Secrets | API key in `.env`, never hardcoded |

**Security test results:**
```
XSS            GET /api/findings/?topic=<script>alert(1)</script> → []
Rate limiting  70 rapid requests vs 60/min limit                  → 12 blocked (429)
```

---

## Data Source

[NIST National Vulnerability Database (NVD)](https://nvd.nist.gov/)
