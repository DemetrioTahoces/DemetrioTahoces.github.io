# AGENTS.md

## Repo overview
- **Type**: Static GitHub Pages site (`demetriotahoces.github.io`) + Serverless API Backend on Vercel.
- **Deploy**: 
  - Front-end: Push to `main` → GitHub Pages serves files at `https://demetriotahoces.github.io/`. No build step.
  - Back-end (Chatbot): Deployed to Vercel via `/CV/Chatbot/vercel.json`.
- **Pages / Structure**:
  - `/index.html` — Root CV landing page. Tailwind CSS (CDN) + Chart.js (CDN). Cyber-neon dark theme.
  - `/FundamentosIA/index.html` — Sub-page for AI adoption strategy roadmap in video intercoms.
  - `/CV/` — Directory containing detailed HTML pages for each past job experience/project, and `/CV/chatbot.html` (the AI assistant UI).
  - `/CV/Chatbot/` — LangGraph (ReAct agent) + FastAPI backend code.
    - `/CV/Chatbot/docs/` — 12 markdown files containing CV information serving as the grounding RAG database.

## Key facts
- **Front-end**: All code is inline in HTML files — no separate CSS/JS bundles, no bundler, no `package.json`, no Node tooling. Dependencies load via CDNs (Tailwind, Phosphor Icons, Google Fonts, marked.js).
- **Back-end**: Python-based FastAPI app using LangGraph and LangChain for a RAG chatbot assistant. Uses Vercel serverless deployment.
- No automated tests, linting, or formatting tooling in root folder.

## Working guidelines
- Edit HTML files directly for the front-end; there is no build or compile step.
- Back-end changes should be made within `/CV/Chatbot/`. Requirements are listed in `requirements.txt`.
- Preview front-end locally with any static server (e.g. `python -m http.server`).
- Maintain the inline style/script pattern for front-end pages — do not introduce a front-end build system unless explicitly requested.
