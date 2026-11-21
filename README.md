# Accessible Client Kanban (Stage 1)

Project 33 (X2: Supplement / AI Coder — Frontend-only Kanban board): Stage-1 client-side Kanban state reducer enforcing the 5-column invariant, contiguous card indexing, keyboard/drag-and-drop moves, and stateless refresh semantics.

## Pinned Attribution

Inspired by and attributed to [`ed-donner/kanban`](https://github.com/ed-donner/kanban).

## Architecture

- **Pure State Reducer (`kanban_stage1/reducer.py`)**: Deterministic, side-effect-free reducer handling card creation, updates, deletions, column moves, and reordering.
- **5-Column Invariant**: Enforces exactly five canonical workflow columns (`backlog`, `todo`, `in_progress`, `review`, `done`) at initialization and across every state transition.
- **Contiguous Card Indexing**: Guarantees `0..N-1` contiguous `order` indices within each column after every insert, move, or delete operation.
- **Keyboard & Drag-and-Drop Parity**: Both pointer drag-and-drop and accessible keyboard moves (`Alt+ArrowLeft/Right/Up/Down`, ARIA live-region announcements) dispatch identical reducer actions.
- **Stateless Refresh Semantics**: Stage 1 operates strictly in-memory on the client without external persistence; page refresh restores the deterministic initial board state.

## 6-Stage Workflow

1. **Stage 1 — Client-Side State Reducer (This Repository)**: Pure state machine, 5-column invariant, contiguous indexing, keyboard/DnD action parity, and stateless refresh semantics.
2. **Stage 2 — Next.js Accessible UI Shell**: React/Next.js board rendering with ARIA landmarks, roving `tabindex`, and screen-reader announcements.
3. **Stage 3 — Local Persistence Adapter**: Optional `localStorage` hydration and schema-versioned state migration.
4. **Stage 4 — Backend API & Database Sync**: REST/tRPC persistence with optimistic updates and conflict detection.
5. **Stage 5 — Multi-User Collaboration**: Real-time presence and WebSocket state synchronization.
6. **Stage 6 — AI Coder Integration**: Automated task triage, card summarization, and acceptance-criteria generation.

## Data Contract

```json
{
  "columns": [
    { "id": "backlog", "title": "Backlog", "cardIds": ["card-1"] },
    { "id": "todo", "title": "To Do", "cardIds": [] },
    { "id": "in_progress", "title": "In Progress", "cardIds": [] },
    { "id": "review", "title": "Review", "cardIds": [] },
    { "id": "done", "title": "Done", "cardIds": [] }
  ],
  "cards": {
    "card-1": {
      "id": "card-1",
      "title": "Define reducer invariants",
      "description": "Enforce 5-column invariant and contiguous indexing.",
      "columnId": "backlog",
      "order": 0
    }
  }
}
```

## Production Controls

- **Invariant Assertions**: Every reducer transition validates column count (`== 5`), unique card IDs, and contiguous `0..N-1` ordering.
- **Input Sanitization & Bounds**: Rejects unknown column IDs, out-of-range target indices (clamped or rejected deterministically), and empty card titles.
- **Accessibility Compliance**: WCAG 2.1 AA keyboard navigation, focus-visible rings, and deterministic ARIA status messages for every move.
- **Zero-Secret Client Bundle**: Stage 1 requires no runtime API keys or backend credentials.

## Local Setup

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
pytest -v
```

## License

MIT — see [LICENSE](LICENSE).
