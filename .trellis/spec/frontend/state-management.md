# State Management

> How application state is managed in the TenCyclesofFate frontend.

---

## Overview

State is managed through **simple global objects** at the top of each JS file. There is no state library, no store pattern, and no reactivity system. State changes are manually followed by `render()` calls.

---

## State Objects

### Main Game (`index.js`)

```javascript
// Primary game state (received from server)
const appState = {
    gameState: null,          // Full session object from backend
    lastRollEventId: null,    // Tracks dice animation deduplication
};

// UI scroll behavior state
const scrollState = {
    animationId: null,
    isUserScrolling: false,
    lastScrollTop: 0,
    scrollTimeout: null,
    isFirstRender: true,      // First render after reconnect → instant scroll
};
```

### Live View (`live.js`)

```javascript
const liveState = {
    liveGameState: null,      // Watched player's state
    playerList: [],           // Active players list
    watchingPlayerId: null,   // Currently watched player's encrypted ID
};
```

---

## State Flow

```
Server (WebSocket) → State Object → render() → DOM
```

### Full State Update

```javascript
case 'full_state':
    appState.gameState = message.data;
    checkAndShowRollEvent();
    render();
    break;
```

### Incremental Patch Update

```javascript
case 'patch':
    if (appState.gameState && message.patch) {
        const result = jsonpatch.applyPatch(appState.gameState, message.patch, true, false);
        appState.gameState = result.newDocument;
        checkAndShowRollEvent();
        render();
    }
    break;
```

---

## State Shape (gameState)

The `appState.gameState` object mirrors the backend session structure:

```javascript
{
    player_id: "username",
    session_date: "2026-02-11",
    opportunities_remaining: 10,     // Number of trials left today
    daily_success_achieved: false,   // Day completed successfully?
    is_in_trial: false,              // Currently in a trial?
    is_processing: false,            // Backend processing an action?
    pending_punishment: null,        // Cheat punishment pending?
    current_life: { ... },           // Current character stats (dynamic keys)
    display_history: ["..."],        // Narrative history (markdown strings)
    roll_event: null,                // Dice roll result (transient)
    redemption_code: null,           // Reward code if day completed
}
```

Note: `internal_history` is stripped by the backend before sending to the client.

---

## Rendering on State Change

Every state change must be followed by a `render()` call. There is no automatic reactivity:

```javascript
function render() {
    if (!appState.gameState) { showLoading(true); return; }
    showLoading(appState.gameState.is_processing);
    DOMElements.opportunitiesSpan.textContent = appState.gameState.opportunities_remaining;
    renderCharacterStatus();
    // ... render display_history, button states, etc.
}
```

---

## Loading States

Loading is controlled by the `is_processing` flag from the backend and local loading state:

```javascript
function showLoading(isLoading) {
    const showFullscreenSpinner = isLoading && !appState.gameState;
    DOMElements.loadingSpinner.style.display = showFullscreenSpinner ? 'flex' : 'none';

    const isProcessing = appState.gameState ? appState.gameState.is_processing : false;
    const buttonsDisabled = isLoading || isProcessing;
    DOMElements.actionInput.disabled = buttonsDisabled;
    DOMElements.actionButton.disabled = buttonsDisabled;
}
```

---

## Common Mistakes to Avoid

1. **Do NOT forget to call `render()`** after modifying state — There is no automatic reactivity
2. **Do NOT mutate `appState.gameState` without reason** — It should only be updated from WebSocket messages
3. **Do NOT introduce a state management library** — Keep the simple global object pattern
4. **Do NOT store derived state** — Compute from `appState.gameState` in render functions
