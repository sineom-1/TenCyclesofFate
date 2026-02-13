# Hook Guidelines

> Custom hook patterns for the TenCyclesofFate project.

---

## Overview

**This project does not use hooks.** There is no React, Vue, or similar framework. The frontend is vanilla JavaScript.

---

## Equivalent Patterns

What would be "hooks" in a framework project are implemented here as:

### Data Fetching → API Object

```javascript
const api = {
    async initGame() {
        const response = await fetch(`${API_BASE_URL}/game/init`, { method: 'POST' });
        if (response.status === 401) throw new Error('Unauthorized');
        if (!response.ok) throw new Error('Failed to initialize game session');
        return response.json();
    },
    async logout() {
        await fetch(`${API_BASE_URL}/logout`, { method: 'POST' });
        window.location.href = '/';
    }
};
```

### WebSocket → Manager Object

```javascript
const socketManager = {
    socket: null,
    connect() { /* ... returns Promise */ },
    sendAction(action) { /* ... sends JSON via WebSocket */ }
};
```

### Side Effects → Plain Functions

```javascript
function setupScrollInterruptListener(element) {
    element.addEventListener('wheel', () => { /* ... */ }, { passive: true });
    element.addEventListener('touchstart', () => { /* ... */ }, { passive: true });
    element.addEventListener('touchend', () => { /* ... */ }, { passive: true });
}
```

---

## Key Takeaway

If you need to add reactive behavior, use the existing patterns:
- **API calls** → Add methods to the `api` object
- **WebSocket messages** → Handle in `socketManager.socket.onmessage` switch
- **DOM interactions** → Add event listeners in `init()` function
- **Timed behavior** → Use `setTimeout` / `setInterval` / `requestAnimationFrame`

Do NOT introduce React hooks or any framework-based hook system.
