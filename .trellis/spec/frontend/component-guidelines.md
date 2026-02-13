# Component Guidelines

> UI component patterns for the TenCyclesofFate project.

---

## Overview

This project uses **vanilla JavaScript** with no component framework. UI "components" are implemented as **render functions** that manipulate the DOM directly. There is no virtual DOM, no component lifecycle, and no template system.

---

## DOM Element Caching Pattern

All DOM references are cached in a `DOMElements` object at the top of each JS file:

**Main game** (`index.js`):
```javascript
const DOMElements = {
    loginView: document.getElementById('login-view'),
    gameView: document.getElementById('game-view'),
    narrativeWindow: document.getElementById('narrative-window'),
    characterStatus: document.getElementById('character-status'),
    actionInput: document.getElementById('action-input'),
    actionButton: document.getElementById('action-button'),
    startTrialButton: document.getElementById('start-trial-button'),
    loadingSpinner: document.getElementById('loading-spinner'),
    // ... more elements
};
```

**Live view** (`live.js`):
```javascript
const DOMElements = {
    playerList: document.getElementById('player-list'),
    narrativeWindow: document.getElementById('narrative-window'),
    characterStatus: document.getElementById('character-status'),
    loadingSpinner: document.getElementById('loading-spinner'),
};
```

---

## Render Function Pattern

Each UI area has a dedicated render function. The main `render()` function orchestrates all updates:

```javascript
function render() {
    if (!appState.gameState) { showLoading(true); return; }
    showLoading(appState.gameState.is_processing);
    DOMElements.opportunitiesSpan.textContent = appState.gameState.opportunities_remaining;
    renderCharacterStatus();
    // Render display_history, update button states...
}
```

### Key Rendering Patterns

**1. DocumentFragment for lists** (prevents reflow):
```javascript
const historyContainer = document.createDocumentFragment();
(appState.gameState.display_history || []).forEach(text => {
    const p = document.createElement('div');
    p.innerHTML = renderMarkdownSafe(text);
    historyContainer.appendChild(p);
});
DOMElements.narrativeWindow.innerHTML = '';
DOMElements.narrativeWindow.appendChild(historyContainer);
```

**2. Recursive rendering for nested objects** (`renderValue`):
```javascript
function renderValue(container, value, level = 0) {
    if (Array.isArray(value)) {
        value.forEach(item => renderValue(container, item, level + 1));
    } else if (typeof value === 'object' && value !== null) {
        // Create nested divs with indentation
    } else {
        // Create text span
    }
}
```

**3. View switching via CSS classes**:
```javascript
function showView(viewId) {
    document.querySelectorAll('.view').forEach(v => v.classList.remove('active'));
    document.getElementById(viewId).classList.add('active');
}
```

---

## XSS Prevention

All markdown content is sanitized before insertion into DOM:

```javascript
function renderMarkdownSafe(markdownText) {
    const rawHtml = marked.parse(markdownText || "", { mangle: false, headerIds: false });
    return DOMPurify.sanitize(rawHtml, {
        USE_PROFILES: { html: true },
        FORBID_TAGS: ["script", "style", "iframe", "object", "embed", "link", "meta"],
        FORBID_ATTR: ["onerror", "onload", "onclick", "onmouseover", "onfocus",
                       "onmouseenter", "onmouseleave", "style"],
    });
}
```

This function exists in both `index.js` and `live.js` (duplicated, not shared).

---

## CSS Layout

The game view uses **CSS Grid** for layout:

```css
#game-view {
    display: grid;
    grid-template-columns: 240px 1fr;
    grid-template-rows: auto 1fr auto;
    grid-template-areas:
        "header header"
        "status main"
        "status action";
}
```

The live view uses a three-column grid:

```css
#live-view.view.active {
    display: grid !important;
    grid-template-columns: 240px 1fr 240px;
    grid-template-areas:
        "header header header"
        "players main status";
}
```

---

## CSS Theming

CSS custom properties define the theme (Jiangnan Garden / 江南园林):

```css
:root {
    --bg-color: #3d2c1d;       /* Dark Wood */
    --panel-bg: rgba(245, 247, 246, 0.9);  /* White Jade */
    --text-color: #3a2e28;
    --primary-color: #6a8b6a;  /* Muted Jade Green */
    --accent-color: #a8453c;   /* Seal Red */
    --font-serif: 'Ma Shan Zheng', 'KaiTi', serif;
    --font-sans: 'ZCOOL KuaiLe', 'Noto Sans SC', sans-serif;
}
```

---

## Event Handling

Events are bound in the `init()` function at the bottom of each JS file:

```javascript
function init() {
    initializeGame();
    setupScrollInterruptListener(DOMElements.narrativeWindow);
    DOMElements.logoutButton.addEventListener('click', handleLogout);
    DOMElements.actionButton.addEventListener('click', () => handleAction());
    DOMElements.actionInput.addEventListener('keydown', (e) => {
        if (e.key === 'Enter') handleAction();
    });
    DOMElements.startTrialButton.addEventListener('click', () => handleAction("开始试炼"));
}
init();
```

---

## Common Mistakes to Avoid

1. **Do NOT use `innerHTML` for user-generated content** — Always use `renderMarkdownSafe()` which sanitizes via DOMPurify
2. **Do NOT query DOM repeatedly** — Cache elements in `DOMElements` object
3. **Do NOT introduce a framework** — Keep vanilla JS
4. **Do NOT add inline event handlers** in HTML — Use `addEventListener` in JS
