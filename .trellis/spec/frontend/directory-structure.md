# Directory Structure

> Frontend code organization for the TenCyclesofFate project.

---

## Overview

The frontend is a **vanilla HTML/CSS/JS** application with **no build system, no bundler, no framework**. It consists of two separate pages served as static files by FastAPI.

---

## Directory Layout

```
frontend/
├── index.html    # Main game page
├── index.js      # Main game logic (ES module)
├── index.css     # Main game styles (Jiangnan Garden theme)
├── live.html     # Live spectator page
├── live.js       # Live spectator logic (ES module)
└── live.css      # Live spectator additional styles
```

---

## Page Architecture

| Page | Files | Purpose |
|------|-------|---------|
| **Main Game** | `index.html` + `index.js` + `index.css` | Player game interface — login, gameplay, actions |
| **Live View** | `live.html` + `live.js` + `live.css` | Spectator mode — watch other players in real-time |

Each page is **self-contained**:
- HTML defines structure
- JS handles all logic (API calls, WebSocket, rendering, state)
- CSS handles all styling

The `live.html` page imports `index.css` as base styles plus `live.css` for overrides.

---

## Serving

Static files are served by FastAPI's `StaticFiles` mount:

```python
# backend/app/main.py
static_files_dir = Path(__file__).parent.parent.parent / "frontend"
app.mount("/", StaticFiles(directory=static_files_dir, html=True), name="static")
```

- `/` serves `frontend/index.html`
- `/live.html` serves `frontend/live.html`
- JS/CSS files are served directly by path

---

## External Dependencies (CDN)

All external libraries are loaded via CDN in HTML `<head>`:

| Library | Version | Purpose |
|---------|---------|---------|
| `marked.js` | latest | Markdown to HTML rendering |
| `DOMPurify` | 3.1.7 | HTML sanitization (XSS prevention) |
| `pako` | 2.1.0 | Gzip decompression for WebSocket messages |
| `fast-json-patch` | 3.1.1 | JSON Patch for incremental state updates (main game only) |

---

## Naming Conventions

- **Files**: `{page-name}.{ext}` — e.g., `index.js`, `live.css`
- **JS Functions**: `camelCase` — e.g., `renderMarkdownSafe`, `handleAction`, `initializeGame`
- **JS Constants**: `UPPER_SNAKE_CASE` — e.g., `API_BASE_URL`
- **CSS Classes/IDs**: `kebab-case` — e.g., `#narrative-window`, `.player-list-item`
- **CSS Variables**: `--kebab-case` — e.g., `--bg-color`, `--panel-bg`, `--primary-color`

---

## Key Architectural Decisions

1. **No framework** — Pure vanilla JS. No React, Vue, or similar.
2. **No build step** — Files are served as-is. No TypeScript, no bundler.
3. **ES modules** — JS files use `type="module"` in script tags.
4. **CDN dependencies** — No `node_modules` or package manager for frontend.
5. **Two separate pages** — Main game and live view are independent HTML documents, not a SPA.

---

## Anti-Patterns to Avoid

- **Do NOT introduce a framework** — Keep vanilla JS.
- **Do NOT add a build system** — No webpack, vite, etc.
- **Do NOT create new HTML pages** without clear justification — Current architecture is two pages.
- **Do NOT use `npm install`** for frontend dependencies — Use CDN links.
