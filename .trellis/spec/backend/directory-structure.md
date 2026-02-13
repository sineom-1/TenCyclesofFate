# Directory Structure

> Backend code organization for the TenCyclesofFate project.

---

## Overview

The backend is a **Python FastAPI** application structured as a single flat package under `backend/app/`. There is no nested module hierarchy — all source files live at the same level, organized by **responsibility domain**.

---

## Directory Layout

```
backend/
├── .env                    # Environment variables (gitignored)
├── requirements.txt        # Python dependencies
└── app/
    ├── __init__.py          # Package marker
    ├── main.py              # FastAPI app instance, routers, endpoints, lifespan
    ├── config.py            # pydantic-settings Settings class
    ├── auth.py              # OAuth2 (Linux.do), JWT creation/validation, FastAPI dependencies
    ├── game_logic.py        # Core game loop, session creation, action processing
    ├── state_manager.py     # File-based session storage (JSON/JSONL), LRU cache, auto-save
    ├── openai_client.py     # OpenAI-compatible API client (chat + image gen), retry, concurrency
    ├── websocket_manager.py # WebSocket connection management, diff/patch, gzip compression
    ├── live_system.py       # Live viewing system (viewer ↔ broadcaster mapping)
    ├── cheat_check.py       # Anti-cheat detection via LLM
    ├── security.py          # Fernet encryption for player ID obfuscation
    ├── redemption.py        # Redemption code generation + database insertion
    ├── db.py                # Raw database connection factory (SQLite / MySQL)
    ├── state.schema.json    # JSON Schema for player session state
    └── prompts/             # LLM prompt templates (plain text)
        ├── game_master.txt
        ├── start_game_prompt.txt
        ├── start_trial_prompt.txt
        └── cheat_check.txt
```

---

## Module Responsibilities

| Module | Responsibility | Key Patterns |
|--------|---------------|--------------|
| `main.py` | App entry, route definitions, WebSocket endpoints | Single file defines ALL routes; uses `APIRouter` with `/api` prefix |
| `config.py` | Configuration via env vars | Single `Settings` instance using `pydantic-settings` |
| `auth.py` | Authentication | OAuth via `authlib`, JWT via `python-jose`, cookie-based auth |
| `game_logic.py` | Game business logic | Largest file (~762 lines); handles game state transitions, AI interactions |
| `state_manager.py` | Persistent storage | File-based (not DB); JSON for metadata, JSONL for histories; LRU cache |
| `openai_client.py` | LLM API calls | Async OpenAI client, exponential backoff retry, per-user semaphore concurrency limit |
| `websocket_manager.py` | Real-time communication | Gzip compression, JSON Patch diffing, debounce |
| `live_system.py` | Spectator mode | Viewer-broadcaster mapping via `defaultdict(set)` |
| `cheat_check.py` | Anti-cheat | Sends player inputs to LLM for analysis, XML response parsing |
| `security.py` | ID encryption | Ephemeral Fernet key (regenerated on restart) |
| `redemption.py` | Reward code generation | Raw SQL INSERT into `redemptions` table |
| `db.py` | DB connection | Factory function supporting SQLite and MySQL |

---

## Naming Conventions

- **Files**: `snake_case.py` — named by domain (e.g., `game_logic.py`, `state_manager.py`)
- **Classes**: `PascalCase` (e.g., `ConnectionManager`, `LiveManager`, `Settings`)
- **Functions**: `snake_case` — private functions prefixed with `_` (e.g., `_load_prompt`, `_extract_json_from_response`)
- **Constants**: `UPPER_SNAKE_CASE` (e.g., `INITIAL_OPPORTUNITIES`, `MAX_CACHED_SESSIONS`)
- **Module-level singletons**: lowercase (e.g., `manager = ConnectionManager()`, `settings = Settings()`)
- **Prompt files**: `snake_case.txt` in `prompts/` directory

---

## Key Architectural Decisions

1. **Flat package structure** — No sub-packages. All modules are siblings under `backend/app/`.
2. **File-based game storage** — Game sessions stored as files (JSON/JSONL) in `game_data/`, NOT in database. Only redemption codes use the database.
3. **Single-file routing** — All routes defined in `main.py`, not split across modules.
4. **Singleton managers** — `websocket_manager`, `live_manager` are module-level singletons imported by other modules.
5. **Prompt templates as text files** — LLM prompts stored in `prompts/` directory, loaded at module init time.

---

## Anti-Patterns to Avoid

- **Do NOT create sub-packages** — Keep the flat structure. New modules go directly in `backend/app/`.
- **Do NOT put routes in separate files** — All route definitions stay in `main.py`.
- **Do NOT use an ORM for game state** — Game state uses the file-based `state_manager`, not a database.
