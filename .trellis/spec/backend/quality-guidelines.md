# Quality Guidelines

> Code quality standards for the TenCyclesofFate backend.

---

## Overview

The project is a Python 3.10+ FastAPI application with no formal test suite or linting configuration. Code quality is maintained through consistent patterns and conventions.

---

## Tech Stack

| Component | Technology |
|-----------|-----------|
| Framework | FastAPI |
| Python | 3.10+ (uses `X | Y` union syntax) |
| Async | `asyncio` throughout |
| Config | `pydantic-settings` |
| Auth | `authlib` (OAuth), `python-jose` (JWT) |
| AI Client | `openai` (AsyncOpenAI) |
| WebSocket | FastAPI native + `jsonpatch` + gzip |
| File I/O | `aiofiles` for async |
| DB | Raw `sqlite3` / `mysql.connector` (no ORM) |

---

## Code Style

### Type Hints

Type hints are used with Python 3.10+ syntax:

```python
# Union types use pipe syntax
def decrypt_player_id(encrypted_id: str) -> str | None:

# dict/list generics use built-in types
_user_semaphores: dict[str, asyncio.Semaphore] = {}
_meta_cache: OrderedDict[str, dict] = OrderedDict()

# FastAPI Annotated pattern for dependencies
current_user: Annotated[dict, Depends(auth.get_current_active_user)]
```

### Async/Await

All I/O operations are async:

```python
async def get_session(player_id: str) -> dict | None:
async def save_session(player_id: str, session_data: dict):
async def get_ai_response(prompt: str, history: list[dict] | None = None, ...) -> str:
```

### Import Organization

Imports follow this order (observed pattern):
1. Standard library (`logging`, `asyncio`, `json`, `time`, etc.)
2. Third-party (`fastapi`, `openai`, `pydantic`, etc.)
3. Local modules (`from . import ...`, `from .config import settings`)

### Module-Level Initialization

Modules initialize singletons and load resources at import time:

```python
# openai_client.py — Client initialized at module level
client: AsyncOpenAI | None = None
if settings.OPENAI_API_KEY and settings.OPENAI_API_KEY != "your_openai_api_key_here":
    client = AsyncOpenAI(...)

# game_logic.py — Prompts loaded at module level
GAME_MASTER_SYSTEM_PROMPT = _load_prompt("game_master.txt")
```

---

## Required Patterns

1. **Module-level logger**: Every module must have `logger = logging.getLogger(__name__)`
2. **Settings from config**: All configuration via `from .config import settings` — never hardcode secrets
3. **Async for I/O**: Use `aiofiles` for file operations, `AsyncOpenAI` for API calls
4. **Private functions**: Prefix with `_` for internal helpers (e.g., `_load_prompt`, `_extract_json_from_response`)
5. **Session state cleanup in `finally`**: Always reset `is_processing` and transient state

---

## Forbidden Patterns

| Pattern | Why Forbidden | Do Instead |
|---------|--------------|------------|
| `print()` for logging | Not captured by logging framework | Use `logger.info/error/...` |
| Hardcoded API keys | Security risk | Use `settings.OPENAI_API_KEY` |
| Synchronous file I/O in async context | Blocks event loop | Use `aiofiles` |
| ORM for game state | Game uses file-based storage | Use `state_manager` functions |
| Global mutable state without module prefix | Hard to trace | Use module-level `_` prefixed vars |
| `time.sleep()` in async code | Blocks event loop | Use `await asyncio.sleep()` |

---

## Concurrency Patterns

### Per-User Semaphore (LLM calls)

```python
MAX_CONCURRENT_REQUESTS_PER_USER = 2
_user_semaphores: dict[str, asyncio.Semaphore] = {}

async def _get_user_semaphore(user_id: str) -> asyncio.Semaphore:
    async with _semaphore_lock:
        if user_id not in _user_semaphores:
            _user_semaphores[user_id] = asyncio.Semaphore(MAX_CONCURRENT_REQUESTS_PER_USER)
        return _user_semaphores[user_id]
```

### Background Tasks

Long-running operations are dispatched via `asyncio.create_task()`:

```python
# game_logic.py — Fire-and-forget game processing
asyncio.create_task(_process_player_action_async(current_user, action))

# game_logic.py — Cancellable delayed tasks
task = asyncio.create_task(_delayed_image_generation(player_id, trigger_time))
_pending_image_tasks[player_id] = task
```

---

## Testing

**No test suite currently exists.** Manual testing is the primary validation method.

To run the server:
```bash
# Development
uvicorn backend.app.main:app --reload

# Production (via run.sh)
uv run python -m uvicorn backend.app.main:app --host 0.0.0.0 --port 8000
```

---

## Running the Application

```bash
# Install dependencies
pip install -r backend/requirements.txt

# Set up environment
cp backend/.env.example backend/.env  # Edit with your settings

# Run development server
uvicorn backend.app.main:app --reload --host 127.0.0.1 --port 8000
```
