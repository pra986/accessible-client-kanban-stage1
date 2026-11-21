# Architecture — Accessible Client Kanban (Stage 1)

## Overview

Stage 1 models a deterministic, frontend-only Kanban board state machine in Python using Pydantic v2 (`pydantic>=2.0.0`). It mirrors the pure client-side state transitions of an accessible Next.js Kanban application without backend persistence.

## Module Layout

- `kanban_stage1/models.py`: Core Pydantic models (`KanbanCard`, `KanbanColumn`, `ClientBoardState`).
- `kanban_stage1/engine.py`: `AccessibleKanbanReducer` implementing pure, validated state transitions and board invariants.
- `kanban_stage1/cli.py`: Runnable CLI demonstration entrypoint exercising board initialization, card creation, drag-and-drop/keyboard moves, column rename, card deletion, and refresh reset.
- `evaluation/eval_cases.json`: Structured evaluation scenarios covering all Stage-1 invariants.
- `tests/test_engine.py`: Pytest suite verifying invariants and edge cases.

## Core Invariants

1. **Fixed 5-Column Invariant**: Every `ClientBoardState` maintains exactly 5 columns (`Backlog`, `To Do`, `In Progress`, `Review`, `Done`). Columns cannot be added or removed in Stage 1.
2. **Contiguous Zero-Indexed Positions**: Within each column, cards are ordered with contiguous `position` values `0, 1, ..., n - 1`, and `column.card_ids` matches that exact order after any drag-and-drop or keyboard move.
3. **Orphan-Free Card Deletion**: Deleting a card removes it from `state.cards` and removes its ID from every column's `card_ids`, re-indexing remaining cards in the affected column.
4. **Non-Empty Column Rename Validation**: Renaming a column strips whitespace and rejects empty or whitespace-only titles with a `ValueError`.
5. **Stateless Refresh Reset Semantics**: Simulating a browser refresh (`refresh_reset`) discards transient in-memory mutations and returns a fresh default 5-column board state.
