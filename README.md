# Agents Playground

A playground for experimenting with the [OpenAI Agents SDK](https://github.com/openai/openai-agents-python). Features a React chat UI and a FastAPI backend with multi-agent handoffs and custom function tools.

## Architecture

```
┌─────────────────────────────────────────────────────────────────────┐
│  Frontend (React + Vite + MUI)                                      │
│  http://localhost:5173                                               │
│                                                                     │
│  ┌───────────────┐    POST /api/chat     ┌───────────────────────┐  │
│  │   Chat UI     │ ──────────────────>   │   FastAPI Backend     │  │
│  │               │ <──────────────────   │   http://localhost:8000│  │
│  └───────────────┘    JSON response      └───────────┬───────────┘  │
└──────────────────────────────────────────────────────┼──────────────┘
                                                       │
                                         Runner.run(triage_agent)
                                                       │
                                                       ▼
┌─────────────────────────────────────────────────────────────────────┐
│  OpenAI Agents SDK                                                  │
│                                                                     │
│  ┌─────────────────────────────────────────────────────────────┐    │
│  │                      Triage Agent                           │    │
│  │          Routes requests to the right specialist            │    │
│  └──────┬───────────────────┬──────────────────────┬───────────┘    │
│         │ handoff            │ handoff               │ handoff       │
│         ▼                   ▼                       ▼              │
│  ┌──────────────┐   ┌──────────────┐   ┌────────────────┐         │
│  │ Math Agent   │   │ History Agent│   │ General Agent  │         │
│  │              │   │              │   │                │         │
│  │ Tools:       │   │ No tools     │   │ No tools      │         │
│  │ - calculate  │   │              │   │                │         │
│  │ - convert_   │   └──────────────┘   └────────────────┘         │
│  │   temperature│                                                  │
│  │ - convert_   │                                                  │
│  │   distance   │                                                  │
│  │ - convert_   │                                                  │
│  │   weight     │                                                  │
│  └──────────────┘                                                  │
│                                                                     │
└─────────────────────────────────────────────────────────────────────┘
                               │
                               ▼
                    ┌─────────────────────┐
                    │   OpenAI API        │
                    │   (LLM calls)       │
                    └─────────────────────┘
```

## Request Flow

```
User types message
       │
       ▼
Frontend sends POST /api/chat { messages: [...] }
       │
       ▼
Backend calls Runner.run(triage_agent, input=messages)
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
result.final_output returned as JSON to frontend
       │
       ▼
UI displays response in chat bubble
```

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
│   ├── main.py              # FastAPI app with CORS
│   └── api/
│       └── endpoints.py     # Chat endpoint, agents, and tools
├── frontend/
│   ├── src/
│   │   ├── App.tsx           # Chat UI component
│   │   ├── App.scss          # Styling
│   │   └── services/
│   │       └── chatService.ts # API client
│   └── package.json
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
