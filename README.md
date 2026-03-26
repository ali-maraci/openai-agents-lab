# Agents Playground

A playground for experimenting with the [OpenAI Agents SDK](https://github.com/openai/openai-agents-python). Features a React chat UI and a FastAPI backend with multi-agent handoffs, custom function tools, guardrails, SSE streaming, and session memory.

## Architecture

```
┌─────────────────────────────────────────────────────────────────────┐
│  Frontend (React + Vite + MUI)                                      │
│  http://localhost:5173                                               │
│                                                                     │
│  ┌───────────────┐  POST /api/chat (SSE)  ┌──────────────────────┐  │
│  │   Chat UI     │ ──────────────────────> │  FastAPI Backend     │  │
│  │               │ <────── token stream ── │  http://localhost:8000│  │
│  └───────────────┘                        └──────────┬───────────┘  │
└──────────────────────────────────────────────────────┼──────────────┘
                                                       │
                                    Runner.run_streamed(triage_agent,
                                         session=SQLiteSession)
                                                       │
                  ┌────────────────────────────────────┼───────────┐
                  │                                    ▼           │
                  │  ┌──────────────────────────────────────────┐  │
                  │  │  Input Guardrails (run in parallel)      │  │
                  │  │  - Prompt injection detector (agent)     │  │
                  │  │  - Inappropriate content checker (agent) │  │
                  │  └──────────────────────────────────────────┘  │
                  │                    │                            │
                  │                    ▼                            │
                  │  ┌──────────────────────────────────────────┐  │
                  │  │            Triage Agent                  │  │
                  │  │    Routes to the right specialist        │  │
                  │  └──────┬──────────┬──────────────┬─────────┘  │
                  │         │ handoff   │ handoff       │ handoff   │
                  │         ▼          ▼              ▼           │
                  │  ┌───────────┐ ┌───────────┐ ┌────────────┐   │
                  │  │Math Agent │ │History    │ │General     │   │
                  │  │           │ │Agent      │ │Agent       │   │
                  │  │Tools:     │ │           │ │            │   │
                  │  │-calculate │ │No tools   │ │No tools    │   │
                  │  │-convert_* │ │           │ │            │   │
                  │  └───────────┘ └───────────┘ └────────────┘   │
                  │                    │                            │
                  │                    ▼                            │
                  │  ┌──────────────────────────────────────────┐  │
                  │  │  Output Guardrail                        │  │
                  │  │  - Sensitive data leakage check (regex)  │  │
                  │  └──────────────────────────────────────────┘  │
                  │                                                │
                  │  OpenAI Agents SDK                              │
                  └────────────────────────────────────────────────┘
                                       │
              ┌────────────────────────┼────────────────────────┐
              ▼                        ▼                        ▼
   ┌─────────────────┐   ┌─────────────────┐   ┌─────────────────┐
   │   OpenAI API    │   │  SQLite Memory  │   │  sessions.db    │
   │   (LLM calls)   │   │  (session store) │   │  (on disk)      │
   └─────────────────┘   └─────────────────┘   └─────────────────┘
```

## Request Flow

```
User types message
       │
       ▼
Frontend sends POST /api/chat { message, session_id } (SSE stream)
       │
       ▼
Backend loads session history from SQLiteSession (sessions.db)
       │
       ▼
Input guardrails run in parallel (prompt injection + content check)
       │
       ▼
Triage Agent ──► OpenAI API (1st call: decide which specialist)
       │
       ▼
Handoff to specialist agent (e.g. Math Agent)
       │
       ▼
Specialist Agent ──► OpenAI API (2nd call: may invoke tools)
       │
       ▼ (if tool used)
Tool runs locally (e.g. calculate("145 * 37") → "5365")
       │
       ▼
Specialist Agent ──► OpenAI API (3rd call: format final answer)
       │
       ▼
Output guardrail checks response for sensitive data
       │
       ▼
Tokens streamed back to frontend via SSE as they arrive
       │
       ▼
Session history saved to SQLiteSession (sessions.db)
       │
       ▼
UI displays tokens in real-time in chat bubble
```

## Features

| Feature | Description |
|---------|-------------|
| **Multi-agent handoffs** | Triage agent routes to Math, History, or General specialist |
| **Function tools** | Calculator and unit converters (temperature, distance, weight) |
| **Input guardrails** | Agent-based prompt injection and content moderation checks |
| **Output guardrails** | Regex-based detection of API keys, tokens, SSNs in responses |
| **SSE streaming** | Token-by-token response streaming with handoff status updates |
| **Session memory** | SQLite-backed conversation history, persists across server restarts |
| **Session expiry** | Expired sessions auto-cleaned on startup (default: 5 days) |

## Session Memory

Conversation history is stored server-side in a SQLite database (`sessions.db`).

- Each browser tab generates a unique `session_id`
- The backend uses `SQLiteSession` from the Agents SDK to store all messages (user + assistant) per session
- On each request, the SDK loads prior conversation from the DB and includes it as context
- Sessions persist across server restarts (file-based, not in-memory)
- **Expiry**: Sessions older than 5 days (based on `updated_at`) are automatically deleted on server startup, along with their messages
- The expiry period is configurable via `SESSION_EXPIRY_DAYS` in `app/api/endpoints.py`

## Setup

### Prerequisites

- Python 3.10+
- Node.js 18+

### Backend

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

Create a `.env` file:

```
OPENAI_API_KEY=your-key-here
```

Run the backend:

```bash
uvicorn app.main:app --reload
```

### Frontend

```bash
cd frontend
npm install
npm run dev
```

Open http://localhost:5173

## Project Structure

```
.
├── app/
│   ├── main.py              # FastAPI app, CORS, session cleanup on startup
│   └── api/
│       └── endpoints.py     # Agents, tools, guardrails, streaming endpoint
├── frontend/
│   ├── src/
│   │   ├── App.tsx           # Chat UI with streaming + session ID
│   │   ├── App.scss          # Styling
│   │   └── services/
│   │       └── chatService.ts # SSE stream consumer
│   └── package.json
├── sessions.db               # SQLite session store (auto-created, gitignored)
├── requirements.txt
└── test.py                   # Standalone agent test script
```

## Tools

| Tool | Description |
|------|-------------|
| `calculate` | Evaluates math expressions (e.g. `2 + 3 * 4`) |
| `convert_temperature` | Converts between Celsius, Fahrenheit, and Kelvin |
| `convert_distance` | Converts between km, miles, meters, and feet |
| `convert_weight` | Converts between kg, lbs, grams, and ounces |

## Guardrails

| Guardrail | Type | Method |
|-----------|------|--------|
| Prompt injection detector | Input | Agent-based classifier |
| Inappropriate content checker | Input | Agent-based classifier |
| Sensitive data leakage | Output | Regex (API keys, AWS keys, GitHub tokens, SSNs) |
