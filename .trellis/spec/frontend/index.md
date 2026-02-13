# Frontend Development Guidelines

> Best practices for frontend development in this project.

---

## Overview

The frontend is a **vanilla HTML/CSS/JS** application — no framework, no build system, no TypeScript. It consists of two self-contained pages (main game + live spectator) served as static files by FastAPI.

---

## Guidelines Index

| Guide | Description | Status |
|-------|-------------|--------|
| [Directory Structure](./directory-structure.md) | File layout, CDN deps, naming conventions | Done |
| [Component Guidelines](./component-guidelines.md) | Render functions, DOM caching, XSS prevention, CSS Grid layout | Done |
| [Hook Guidelines](./hook-guidelines.md) | N/A — vanilla JS equivalent patterns (API object, socketManager) | Done |
| [State Management](./state-management.md) | Global state objects, WebSocket-driven updates, render cycle | Done |
| [Quality Guidelines](./quality-guidelines.md) | Required/forbidden patterns, CSS conventions, security checklist | Done |
| [Type Safety](./type-safety.md) | N/A — no TypeScript; implicit type contracts via JSON Schema | Done |

---

## Quick Reference

- **Tech**: Vanilla JS (ES modules) + Plain CSS + CDN libraries
- **Pages**: `index.html` (game) + `live.html` (spectator)
- **State**: Simple global objects → `render()` → DOM
- **Security**: DOMPurify for all rendered content, HttpOnly cookie auth
- **Theme**: Jiangnan Garden (江南园林) — CSS custom properties

---

**Language**: All documentation should be written in **English**.
