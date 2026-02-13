# Quality Guidelines

> Code quality standards for the TenCyclesofFate frontend.

---

## Overview

The frontend is vanilla HTML/CSS/JS with no build tools, no linting, and no test suite. Quality is maintained through consistent patterns and manual testing.

---

## Tech Stack

| Component | Technology |
|-----------|-----------|
| Language | Vanilla JavaScript (ES modules) |
| Styling | Plain CSS with custom properties |
| Markdown | marked.js (CDN) |
| Sanitization | DOMPurify (CDN) |
| Compression | pako (CDN) |
| Patching | fast-json-patch (CDN) |
| Analytics | Microsoft Clarity |

---

## Code Organization Pattern

Each JS file follows the same structure:

```
1. Constants (API_BASE_URL, etc.)
2. State Objects (appState, scrollState, etc.)
3. DOM Element Cache (DOMElements object)
4. API Client (api object)
5. WebSocket Manager (socketManager object)
6. UI & Rendering Functions
7. Event Handlers
8. Initialization (init function, called at bottom)
```

---

## Required Patterns

1. **XSS Prevention**: ALL markdown/user content must go through `renderMarkdownSafe()`:
   ```javascript
   p.innerHTML = renderMarkdownSafe(text);  // CORRECT
   p.innerHTML = text;                       // FORBIDDEN
   ```

2. **DOM Caching**: All frequently-accessed DOM elements in `DOMElements` object

3. **WebSocket Binary Mode**: Always set `binaryType = 'arraybuffer'` and handle gzip decompression:
   ```javascript
   this.socket.binaryType = 'arraybuffer';
   // In onmessage:
   if (event.data instanceof ArrayBuffer) {
       const decompressed = pako.ungzip(new Uint8Array(event.data), { to: 'string' });
       message = JSON.parse(decompressed);
   }
   ```

4. **Reconnection**: WebSocket auto-reconnects with 5-second delay:
   ```javascript
   this.socket.onclose = () => {
       showLoading(true);
       setTimeout(() => this.connect(), 5000);
   };
   ```

5. **Passive event listeners** for scroll/touch events:
   ```javascript
   element.addEventListener('wheel', handler, { passive: true });
   ```

---

## Forbidden Patterns

| Pattern | Why | Do Instead |
|---------|-----|------------|
| `innerHTML = userContent` | XSS vulnerability | Use `renderMarkdownSafe()` |
| `document.getElementById()` in hot paths | Performance | Use cached `DOMElements` |
| Inline `<script>` for app logic | Unmaintainable | Use separate `.js` file with `type="module"` |
| `npm install` for frontend deps | No build system | Use CDN `<script>` tags |
| Framework code (React/Vue) | Architectural mismatch | Vanilla JS only |

---

## CSS Conventions

### Custom Properties (Theme)

All colors, fonts, and spacing use CSS custom properties:

```css
:root {
    --bg-color: #3d2c1d;
    --panel-bg: rgba(245, 247, 246, 0.9);
    --primary-color: #6a8b6a;
    --accent-color: #a8453c;
    --font-serif: 'Ma Shan Zheng', 'KaiTi', serif;
    --font-sans: 'ZCOOL KuaiLe', 'Noto Sans SC', sans-serif;
}
```

### Responsive Design

Mobile breakpoint at `850px` (main game) and `1000px` (live view):

```css
@media (max-width: 850px) {
    #game-view {
        grid-template-columns: 1fr;
        grid-template-areas: "header" "status" "main" "action";
    }
}
```

### Utility Classes

```css
.hidden { display: none !important; }
.view { display: none; }
.view.active { display: flex; }
```

---

## Security Checklist

- [x] DOMPurify sanitizes all rendered markdown
- [x] Forbidden tags: script, style, iframe, object, embed, link, meta
- [x] Forbidden attributes: all event handlers (onerror, onclick, etc.) and style
- [x] WebSocket auth via HttpOnly cookie (not URL token)
- [x] Encrypted player IDs in live view (Fernet, server-side)

---

## Testing

**No automated test suite.** Testing is manual:

1. Open `http://localhost:8000/` for the main game
2. Open `http://localhost:8000/live.html` for live view
3. Test WebSocket reconnection by toggling network
4. Test responsive layout by resizing browser
