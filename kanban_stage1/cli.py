"""Runnable CLI demonstration entrypoint for Accessible Client Kanban (Stage 1)."""

from __future__ import annotations

import json

from kanban_stage1.engine import AccessibleKanbanReducer


def run_demo() -> dict:
    """Execute a full Stage-1 board lifecycle and return summary metadata."""
    state = AccessibleKanbanReducer.create_initial_board()
    state = AccessibleKanbanReducer.add_card(
        state, "col-1", "Audit ARIA landmarks", "Ensure keyboard focus rings", card_id="c1"
    )
    state = AccessibleKanbanReducer.add_card(
        state, "col-1", "Implement keyboard move", "Support arrow keys", card_id="c2"
    )
    state = AccessibleKanbanReducer.keyboard_move_card(state, "c1", "right")
    state = AccessibleKanbanReducer.move_card(state, "c2", "col-3", 0)
    state = AccessibleKanbanReducer.rename_column(state, "col-2", "Ready for Dev")
    state = AccessibleKanbanReducer.delete_card(state, "c1")

    summary = {
        "column_count": len(state.columns),
        "columns": [
            {"id": col.id, "title": col.title, "card_ids": col.card_ids}
            for col in state.columns
        ],
        "remaining_cards": list(state.cards.keys()),
    }

    reset_state = AccessibleKanbanReducer.refresh_reset(state)
    summary["after_refresh_card_count"] = len(reset_state.cards)
    summary["after_refresh_column_count"] = len(reset_state.columns)
    return summary


def main() -> None:
    """CLI entrypoint."""
    print(json.dumps(run_demo(), indent=2))


if __name__ == "__main__":
    main()
