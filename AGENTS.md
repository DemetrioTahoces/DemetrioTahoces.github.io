# AGENTS.md

## Repo overview
- **Type**: Static GitHub Pages site (`<username>.github.io`).
- **Deploy**: Push to `main` → GitHub Pages serves files at `https://demetriotahoces.github.io/`. No build step.
- **Pages**:
  - `/index.html` — Root page. Tailwind CSS (CDN) + Chart.js (CDN). Cyber-neon dark theme.
  - `/FundamentosIA/index.html` — Sub-page. Inline CSS with CSS variables, Phosphor Icons (CDN).

## Key facts
- All code is inline in HTML files — no separate CSS/JS bundles, no bundler, no `package.json`, no Node tooling.
- External dependencies load via CDN script/link tags (Tailwind, Chart.js, Phosphor Icons, Google Fonts).
- Spanish-language content about AI adoption strategy for video intercom systems.
- No tests, lint, formatter, or typecheck config exists.

## Working guidelines
- Edit HTML files directly; there is no build or compile step.
- Preview locally with any static server (e.g. `python -m http.server` or VS Code Live Server).
- Maintain the inline style/script pattern — do not introduce a build system unless explicitly requested.
