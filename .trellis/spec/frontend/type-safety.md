# Type Safety

> Type patterns for the TenCyclesofFate frontend.

---

## Overview

**This project does not use TypeScript.** The frontend is plain JavaScript with no type system, no JSDoc type annotations, and no type checking.

---

## Implicit Type Contracts

Types are enforced implicitly through:

### 1. WebSocket Message Protocol

Messages from the server follow these structures:

```
{ type: "full_state", data: SessionObject }
{ type: "patch", patch: JsonPatchArray }
{ type: "live_update", data: SessionObject }
{ type: "error", detail: string }
```

### 2. Session Object Shape

Defined in `backend/app/state.schema.json` and enforced by the backend. Key fields:

| Field | Type | Description |
|-------|------|-------------|
| `player_id` | string | Player username |
| `opportunities_remaining` | integer | Trials remaining |
| `is_in_trial` | boolean | In active trial |
| `is_processing` | boolean | Backend processing |
| `current_life` | object \| null | Character data (dynamic keys) |
| `display_history` | string[] | Narrative history |
| `roll_event` | object \| null | Dice roll data |

### 3. API Responses

```
POST /api/game/init → SessionObject
GET /api/live/players → Array<{ player_id, display_name, last_modified }>
```

---

## Defensive Patterns Used

Since there are no compile-time type checks, the code uses runtime guards:

```javascript
// Optional chaining
const rollEvent = appState.gameState?.roll_event;

// Default values
(appState.gameState.display_history || []).forEach(...)

// Type checking before operations
if (text.startsWith('> ')) p.classList.add('user-input-message');
```

---

## Key Takeaway

Do NOT introduce TypeScript to this project. If type documentation is needed, use comments inline. The backend's `state.schema.json` serves as the canonical type reference for the session object.
