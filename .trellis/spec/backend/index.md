# Backend Development Guidelines

> Best practices for backend development in this project.

---

## Overview

The backend is a **Python 3.10+ FastAPI** application with async throughout. It uses file-based storage for game sessions, raw SQL for redemption codes, and OpenAI-compatible APIs for game AI and image generation.

---

## Guidelines Index

| Guide | Description | Status |
|-------|-------------|--------|
| [Directory Structure](./directory-structure.md) | Flat package layout, module responsibilities, naming conventions | Done |
| [Database Guidelines](./database-guidelines.md) | Dual storage (file-based + SQL), connection management, JSONL patterns | Done |
| [Error Handling](./error-handling.md) | HTTPException, try/except logging, narrative errors, finally cleanup | Done |
| [Quality Guidelines](./quality-guidelines.md) | Tech stack, code style, concurrency patterns, forbidden patterns | Done |
| [Logging Guidelines](./logging-guidelines.md) | Per-module logger, log levels, language conventions | Done |

---

## Quick Reference

- **Framework**: FastAPI + uvicorn
- **Storage**: File-based (game sessions in `game_data/`), MySQL/SQLite (redemption codes only)
- **Auth**: OAuth2 (Linux.do) + JWT in HttpOnly cookies
- **AI**: AsyncOpenAI with retry, per-user semaphore concurrency limit
- **Real-time**: WebSocket with gzip compression + JSON Patch diffing

---

**Language**: All documentation should be written in **English**.
