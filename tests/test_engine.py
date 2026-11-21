"""Pytest suite for AccessibleKanbanReducer and Stage-1 Kanban invariants."""

import pytest
from pydantic import ValidationError

from kanban_stage1.engine import AccessibleKanbanReducer
from kanban_stage1.models import COLUMN_COUNT, ClientBoardState, KanbanColumn


def test_five_column_count_invariant() -> None:
    state = AccessibleKanbanReducer.create_initial_board()
    assert len(state.columns) == COLUMN_COUNT == 5
    assert [col.title for col in state.columns] == [
        "Backlog",
        "To Do",
        "In Progress",
        "Review",
        "Done",
    ]

    with pytest.raises(ValidationError):
        ClientBoardState(
            columns=[
                KanbanColumn(id="col-1", title="Only One", position=0, card_ids=[])
            ]
        )


def test_contiguous_card_positions_after_arbitrary_moves() -> None:
    state = AccessibleKanbanReducer.create_initial_board()
    state = AccessibleKanbanReducer.add_card(state, "col-1", "Task A", card_id="a")
    state = AccessibleKanbanReducer.add_card(state, "col-1", "Task B", card_id="b")
    state = AccessibleKanbanReducer.add_card(state, "col-1", "Task C", card_id="c")

    # Drag-and-drop move within and across columns
    state = AccessibleKanbanReducer.move_card(state, "c", "col-1", 0)
    assert state.columns[0].card_ids == ["c", "a", "b"]
    assert [state.cards[cid].position for cid in state.columns[0].card_ids] == [0, 1, 2]

    state = AccessibleKanbanReducer.move_card(state, "a", "col-3", 0)
    assert state.columns[0].card_ids == ["c", "b"]
    assert [state.cards[cid].position for cid in state.columns[0].card_ids] == [0, 1]
    assert state.columns[2].card_ids == ["a"]
    assert state.cards["a"].position == 0

    # Keyboard move right and down
    state = AccessibleKanbanReducer.keyboard_move_card(state, "c", "right")
    state = AccessibleKanbanReducer.keyboard_move_card(state, "b", "right")
    state = AccessibleKanbanReducer.keyboard_move_card(state, "b", "up")
    assert state.columns[1].card_ids == ["b", "c"]
    assert [state.cards[cid].position for cid in state.columns[1].card_ids] == [0, 1]


def test_clean_card_deletion_removes_id_from_column_lists() -> None:
    state = AccessibleKanbanReducer.create_initial_board()
    state = AccessibleKanbanReducer.add_card(state, "col-2", "First", card_id="c1")
    state = AccessibleKanbanReducer.add_card(state, "col-2", "Second", card_id="c2")
    state = AccessibleKanbanReducer.add_card(state, "col-2", "Third", card_id="c3")

    state = AccessibleKanbanReducer.delete_card(state, "c2")
    assert "c2" not in state.cards
    assert all("c2" not in col.card_ids for col in state.columns)
    assert state.columns[1].card_ids == ["c1", "c3"]
    assert [state.cards[cid].position for cid in state.columns[1].card_ids] == [0, 1]


def test_empty_column_title_rejection() -> None:
    state = AccessibleKanbanReducer.create_initial_board()
    for bad_title in ("", "   ", "\t\n"):
        with pytest.raises(ValueError, match="non-empty"):
            AccessibleKanbanReducer.rename_column(state, "col-1", bad_title)

    renamed = AccessibleKanbanReducer.rename_column(state, "col-1", "  Triage  ")
    assert renamed.columns[0].title == "Triage"


def test_stateless_refresh_reset_semantics() -> None:
    state = AccessibleKanbanReducer.create_initial_board()
    state = AccessibleKanbanReducer.add_card(state, "col-1", "Ephemeral", card_id="tmp")
    state = AccessibleKanbanReducer.rename_column(state, "col-1", "Custom")

    reset_state = AccessibleKanbanReducer.refresh_reset(state)
    assert len(reset_state.columns) == 5
    assert reset_state.columns[0].title == "Backlog"
    assert reset_state.cards == {}
    assert all(col.card_ids == [] for col in reset_state.columns)
