# Logging Guidelines

> How logging is done in the TenCyclesofFate project.

---

## Overview

The project uses Python's built-in `logging` module. Each module creates its own logger. Configuration is minimal — `basicConfig` at `INFO` level in `main.py`.

---

## Setup Pattern

### Configuration (in `main.py`)

```python
logging.basicConfig(level=logging.INFO)
```

### Per-Module Logger (every module)

```python
logger = logging.getLogger(__name__)
```

This pattern is consistent across ALL backend modules:
- `main.py`, `game_logic.py`, `state_manager.py`, `openai_client.py`
- `websocket_manager.py`, `live_system.py`, `cheat_check.py`
- `security.py`, `redemption.py`, `db.py`

---

## Log Levels in Practice

| Level | Usage | Examples |
|-------|-------|---------|
| `DEBUG` | Detailed internal state, cache operations, concurrency info | `logger.debug(f"用户 {user_id} 获取LLM请求槽位")` |
| `INFO` | Normal operations, lifecycle events, successful actions | `logger.info(f"Starting new daily session for {player_id}.")` |
| `WARNING` | Non-critical issues, blocked actions, expected failures | `logger.warning(f"Action '{action}' blocked for {player_id}, processing.")` |
| `ERROR` | Failures requiring attention, with stack traces | `logger.error(f"Error processing action: {e}", exc_info=True)` |

---

## Logging Patterns by Context

### Application Lifecycle

```python
logging.info("Application startup...")
logging.info("Application shutdown...")
logger.info(f"文件存储初始化完成，当前 {len(_sessions_index)} 个会话")
```

### Player Actions

```python
logger.info(f"Starting new daily session for {player_id}.")
logger.warning(f"Action '{action}' blocked for {player_id}, processing.")
logger.warning(f"Player {player_id} tried to start trial with 0 opportunities.")
```

### External API Calls

```python
logger.info("OpenAI 客户端初始化成功。")
logger.error(f"OpenAI API 错误 (尝试 {attempt + 1}/{max_retries}): {e}")
logger.error(f"联系OpenAI时发生意外错误 (尝试 {attempt + 1}/{max_retries}): {e}")
```

### Database Operations

```python
logger.info(f"Successfully connected to SQLite database at: {db_path}")
logger.error(f"Database connection failed to '{settings.DATABASE_URL}': {e}", exc_info=True)
logger.info(f"Successfully inserted redemption code '{redemption_key}' for user '{user_id}'")
```

### Security / Anti-Cheat

```python
logger.info(f"Running batched cheat check for player {player_id} on {len(inputs_to_check)} inputs.")
logger.warning(f"Cheat detected for player {player_id}! Level: {level}. Reason: {reason}.")
logger.info(f"玩家 {player_id} 被标记为 {level} 惩罚，原因: {reason}")
```

### WebSocket

```python
logger.info(f"Player '{player_id}' connected via WebSocket.")
logger.info(f"Player '{player_id}' disconnected from WebSocket.")
logger.warning(f"WebSocket for player '{player_id}' disconnected: {e}")
```

---

## Language Convention

Log messages use a **mixed language** approach:
- **English** for technical/structural messages (WebSocket, API, auth)
- **Chinese** for game-domain messages (session management, cheat detection, image generation)

This is the existing convention. New code should follow the same pattern based on context.

---

## Error Logging Best Practices (Existing)

Always include `exc_info=True` for error-level logs to capture stack traces:

```python
logger.error(f"Error processing action for {player_id}: {e}", exc_info=True)
```

For critical paths, also log the full traceback explicitly:

```python
logger.error(f"Full traceback:\n{traceback.format_exc()}")
```

---

## What NOT to Log

- **Player session content** — Never log full `internal_history` or `display_history`
- **API keys / secrets** — Never log `OPENAI_API_KEY`, `SECRET_KEY`, etc.
- **Full redemption codes** in high-volume logs (OK in INFO-level generation logs)
- **Binary WebSocket data** — Only log metadata, not payloads

---

## Common Mistakes to Avoid

1. **Do NOT use `print()`** — Always use `logger` from the module-level logger
2. **Do NOT forget `exc_info=True`** on `logger.error()` calls — Stack traces are essential for debugging
3. **Do NOT log at INFO level for per-request operations in hot paths** — Use DEBUG for high-frequency events (e.g., WebSocket messages, cache hits)
