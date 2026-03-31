# OpenAI Agents Lab — Eval & Observability First Platform

## Motivation

Most agent demos focus on "it works" rather than:
- why it works
- when it fails
- how to improve it
- how to measure progress

Modern agent engineering is shifting toward:
- traceability
- evaluation-driven development
- reproducibility
- controlled experimentation

This project upgrades `openai-agents-lab` into a platform where:
- every run is traceable
- every change is measurable
- every failure is diagnosable
- every improvement is validated

---

## Goal

Build an agent platform that answers:

1. What happened? → Full trace  
2. How good was it? → Eval scores  
3. Why did it fail? → Failure diagnostics  
4. Did this change improve things? → Experiment comparison  

---

## Scope

### v1 — Observability-first
- Trace every run
- Inspect tool calls and handoffs
- Track latency and cost

### v2 — Eval-first
- Benchmark datasets
- Automated graders
- Regression testing

### v3 — Production-ready
- Versioned agents
- Release gating
- Monitoring + alerts

---

## Architecture

### Backend
- Python + FastAPI
- OpenAI Responses API / Agents SDK
- PostgreSQL / SQLite
- Tracing layer (Phoenix or custom)

### Frontend
- React + TypeScript
- Trace viewer
- Eval dashboard
- Experiment comparison

---

## Core Concepts

### Run
A single agent execution:
- input
- agent version
- trace
- output
- metrics

### Trace
Structured sequence of events:
- model calls
- tool calls
- handoffs
- retries

### Eval
Scoring mechanism:
- correctness
- tool usage
- latency
- cost

### Experiment
Comparison between versions:
- baseline vs candidate
- regression detection

---

## Data Model

### Run
- run_id
- agent_version
- model
- input
- output
- latency
- cost
- tokens

### Trace Span
- span_id
- type (model/tool/handoff)
- start/end time
- duration
- metadata

### Eval Result
- score
- pass/fail
- reason

---

## API

### POST /runs
Execute agent run

### GET /runs
List runs

### GET /runs/{id}
View trace and results

### POST /evals/run
Run evaluations

### GET /evals/summary
Aggregate metrics

### POST /experiments/compare
Compare versions

---

## Observability Design

Track:
- model calls
- tool calls
- retries
- failures
- handoffs

Metrics:
- latency
- cost
- tool success rate
- failure types

Failure Tags:
- bad_tool_choice
- schema_error
- hallucination
- looping
- timeout

---

## Evaluation Design

Benchmark dataset:
- tool routing
- retrieval QA
- structured outputs
- safety/refusal
- robustness

Grader types:
- exact match
- rubric scoring
- trajectory evaluation

Metrics:
- pass rate
- cost
- latency
- tool efficiency

---

## UX Design

### Runs Page
- list runs
- metrics overview

### Run Detail
- trace timeline
- tool breakdown
- eval scores

### Compare Page
- baseline vs candidate
- regression summary

### Dashboard
- pass rates
- failure trends
- cost/latency

---

## Implementation Phases

### Phase 0 — Refactor
- define schemas
- persist runs
- standardize tools

### Phase 1 — Tracing
- capture spans
- build trace viewer

### Phase 2 — Benchmarks
- dataset schema
- seed tasks

### Phase 3 — Eval Engine
- graders
- scoring

### Phase 4 — Experiments
- compare versions
- regression checks

### Phase 5 — UI
- runs page
- trace explorer
- dashboard

### Phase 6 — Versioning
- agent registry
- prompt versions

### Phase 7 — Monitoring
- alerts
- drift detection

---

## Timeline (8 weeks)

Week 1: Refactor  
Week 2: Tracing  
Week 3: Benchmarks  
Week 4: Eval engine  
Week 5: Experiments  
Week 6: UI  
Week 7: Versioning  
Week 8: Monitoring + polish  

---

## Deliverables

### Milestone A
Traceable agent system

### Milestone B
Eval-first benchmarking

### Milestone C
Experiment comparison

### Milestone D
Production-ready platform

---

## First GitHub Issues

1. Refactor runtime  
2. Define trace schema  
3. Instrument tools  
4. Build runs API  
5. Create benchmark dataset  
6. Implement graders  
7. Add eval pipeline  
8. Build compare tool  
9. Build trace UI  
10. Build dashboard  
11. Add version registry  
12. Add monitoring  

---

## Risks

- Overengineering UI → keep simple  
- Weak evals → start narrow  
- No reproducibility → version everything  

---

## Definition of Done

- Runs are traceable  
- Evals are automated  
- Experiments are comparable  
- Failures are diagnosable  
- System is reproducible  

---

## MVP

- Trace capture  
- Benchmark dataset  
- Eval scoring  
- Compare versions  
- Simple dashboard  

---

## Summary

This project demonstrates:
- agent orchestration
- evaluation-driven development
- observability engineering
- production readiness

A strong portfolio piece for AI engineer roles.
