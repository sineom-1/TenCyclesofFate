# Error Handling

> How errors are handled in the TenCyclesofFate project.

---

## Overview

Error handling follows a **defensive, graceful-degradation** approach. Since this is a game, errors are often wrapped in narrative-style messages to maintain immersion. Critical errors are logged but rarely crash the application.

---

## Error Handling Patterns

### 1. FastAPI HTTP Exceptions

Used for authentication and API-level errors in `auth.py` and `main.py`:

```python
# auth.py — Standard credentials exception
credentials_exception = HTTPException(
    status_code=status.HTTP_401_UNAUTHORIZED,
    detail="Could not validate credentials",
    headers={"WWW-Authenticate": "Bearer"},
)
```

```python
# main.py — OAuth callback error
except Exception as e:
    logger.error(f"Error during OAuth callback: {e}")
    raise HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not authorize access token",
    )
```

### 2. Try/Except with Logging (Primary Pattern)

Most functions use broad `try/except` blocks with `logger.error()`:

```python
# game_logic.py — Main game loop error handling
try:
    # ... game logic ...
except Exception as e:
    logger.error(f"Error processing action for {player_id}: {e}", exc_info=True)
    logger.error(f"Full traceback:\n{traceback.format_exc()}")
    # Append narrative error message to player's display
    session["display_history"].append(
        "【天机紊乱】\n\n虚空微微震颤..."
    )
```

### 3. Return None on Failure

Functions that may fail return `None` instead of raising exceptions:

```python
# db.py
def get_db_connection():
    try:
        # ... connect ...
        return conn
    except (sqlite3.Error, mysql.connector.Error) as e:
        logger.error(f"Database connection failed: {e}", exc_info=True)
        return None  # Caller checks for None

# redemption.py
def generate_and_insert_redemption_code(...) -> str | None:
    # Returns None on any failure

# security.py
def decrypt_player_id(encrypted_id: str) -> str | None:
    # Returns None on decryption failure
```

### 4. Error Strings for AI Client

The OpenAI client returns error strings prefixed with `"错误："`:

```python
# openai_client.py
if not client:
    return "错误：OpenAI客户端未初始化。..."

# Caller checks for error prefix:
if ai_json_response_str.startswith("错误："):
    raise Exception(f"OpenAI Client Error: {ai_json_response_str}")
```

### 5. Graceful Game Narrative Errors

When game processing fails, the error is presented as an in-game narrative:

```python
# game_logic.py — Error shown as game narrative
session["display_history"].append(
    "【天机紊乱】\n\n"
    "虚空微微震颤，汝之行动仿佛被一股无形之力化解...\n\n"
    "天道运转偶有滞涩，此非汝之过。请稍候片刻，再作尝试。"
)
```

### 6. `finally` for State Cleanup

Game logic uses `finally` blocks to ensure session state is always cleaned up:

```python
# game_logic.py
finally:
    try:
        session = await state_manager.get_session(player_id)
        if session:
            session["roll_event"] = None
            session["is_processing"] = False
            await state_manager.save_session(player_id, session)
    except Exception as e:
        logger.error(f"Error resetting session state: {e}", exc_info=True)
```

---

## WebSocket Error Handling

WebSocket disconnections are handled via specific exception types:

```python
# main.py
except WebSocketDisconnect:
    websocket_manager.disconnect(username)

# websocket_manager.py
except (WebSocketDisconnect, RuntimeError) as e:
    logger.warning(f"WebSocket for player '{player_id}' disconnected: {e}")
    self.disconnect(player_id)
```

---

## 404 Handler

All unmatched routes redirect to the root page:

```python
@app.exception_handler(404)
async def not_found_handler(request: Request, exc: HTTPException):
    return RedirectResponse(url="/")
```

---

## API Error Response Format

No standardized error response schema exists. Errors are returned via:
- `HTTPException` with `detail` string for HTTP endpoints
- WebSocket `error` message type: `{"type": "error", "detail": "..."}`
- Narrative strings for game state errors

---

## Common Mistakes to Avoid

1. **Do NOT let game errors crash the server** — Always wrap game logic in try/except and show narrative error messages
2. **Do NOT forget `exc_info=True`** — Always include traceback info in `logger.error()` calls for debugging
3. **Do NOT raise exceptions from `state_manager`** — File I/O errors are caught and logged, returning `None`
4. **Do NOT forget to reset `is_processing`** — Always reset in `finally` block; a stuck `is_processing=True` locks the player out
