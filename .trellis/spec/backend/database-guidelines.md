# Database Guidelines

> Database patterns and conventions for the TenCyclesofFate project.

---

## Overview

This project uses a **dual storage strategy**:

1. **File-based storage** (`state_manager.py`) — For game session data (the primary data store)
2. **Relational database** (`db.py` + `redemption.py`) — Only for redemption codes, connecting to an external MySQL/SQLite database

No ORM is used. Database access is via **raw SQL** with `sqlite3` / `mysql.connector`.

---

## Storage Architecture

### Game Sessions (File-Based)

Game state is stored in `game_data/` as individual files per player:

```
game_data/
├── index.json                    # player_id -> last_modified mapping
└── sessions/
    └── {player_id}/
        ├── meta.json             # Session metadata (everything except histories)
        ├── internal_history.jsonl # LLM conversation history (one JSON object per line)
        └── display_history.jsonl  # Player-visible narrative (one JSON string per line)
```

**Key patterns:**
- Histories use **JSONL** (append-only) for performance — new entries are appended, not rewritten
- Metadata uses **JSON** (full rewrite on each save)
- **LRU cache** (`OrderedDict`) for metadata with `MAX_CACHED_SESSIONS = 5`
- **Auto-save** for index every 5 minutes
- **Session expiration**: sessions older than 3 days are auto-cleaned on startup

**Example — Reading a session** (from `state_manager.py`):
```python
async def get_session(player_id: str) -> dict | None:
    meta = await _load_meta(player_id)
    if not meta:
        return None
    internal_history = await _read_jsonl_file(_get_internal_history_path(player_id))
    display_history = await _read_jsonl_file(_get_display_history_path(player_id))
    session = meta.copy()
    session["internal_history"] = internal_history
    session["display_history"] = display_history
    return session
```

**Example — Saving a session** (incremental append for histories):
```python
# Only append new items to JSONL files
if new_count > old_internal_count:
    new_items = internal_history[old_internal_count:]
    for item in new_items:
        await _append_jsonl_file(path, item)
```

### Relational Database (Redemption Codes Only)

Used exclusively by `redemption.py` for inserting reward codes.

**Connection pattern** (from `db.py`):
```python
def get_db_connection():
    db_url = settings.DATABASE_URL
    parsed_url = urlparse(db_url)
    if parsed_url.scheme == "sqlite":
        conn = sqlite3.connect(db_path)
        return conn
    elif parsed_url.scheme == "mysql":
        conn = mysql.connector.connect(...)
        return conn
```

**Query pattern** (from `redemption.py`):
```python
conn = db.get_db_connection()
cursor = conn.cursor()
cursor.execute(
    "INSERT INTO redemptions (user_id, `key`, status, name, quota, created_time) VALUES (%s, %s, %s, %s, %s, %s)",
    (user_id, redemption_key, 1, name, int(quota), current_timestamp)
)
conn.commit()
```

---

## Connection Management

- **No connection pooling** — Each database call creates a new connection and closes it in `finally`
- **Manual transaction management** — Explicit `conn.commit()` and `conn.rollback()`
- **Always close in `finally`** block

```python
conn = None
try:
    conn = db.get_db_connection()
    # ... operations ...
    conn.commit()
except Exception as e:
    if conn:
        conn.rollback()
finally:
    if conn:
        conn.close()
```

---

## Naming Conventions

- **Table names**: lowercase plural (e.g., `redemptions`)
- **Column names**: `snake_case` (e.g., `user_id`, `created_time`)
- **Backtick reserved words**: MySQL reserved words are backtick-quoted (e.g., `` `key` ``)

---

## Migrations

**No migration system exists.** The database schema is managed externally. The `redemptions` table schema is:

| Column | Type | Description |
|--------|------|-------------|
| `user_id` | int | User's external ID |
| `key` | string | UUID hex redemption code |
| `status` | int | Status flag (1 = active) |
| `name` | string | Descriptive name |
| `quota` | int | Converted value |
| `created_time` | int | Unix timestamp |

---

## Common Mistakes to Avoid

1. **Do NOT use the database for game state** — All game session data goes through `state_manager.py` file storage
2. **Do NOT forget to close connections** — Always use `try/finally` pattern
3. **Do NOT assume MySQL** — Code must support both SQLite and MySQL via `DATABASE_URL` scheme detection
4. **Do NOT use parameterized queries with `?`** — Use `%s` placeholders (mysql.connector style)
