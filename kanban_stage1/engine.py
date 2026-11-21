"""Pure client-side state reducer for the Stage-1 accessible Kanban board."""

from __future__ import annotations

from typing import Literal, Optional
from uuid import uuid4

from kanban_stage1.models import (
    COLUMN_COUNT,
    DEFAULT_COLUMN_TITLES,
    ClientBoardState,
    KanbanCard,
    KanbanColumn,
)

KeyboardDirection = Literal["up", "down", "left", "right"]


class AccessibleKanbanReducer:
    """Enforces all Stage-1 Kanban board invariants across pure state transitions."""

    @classmethod
    def create_initial_board(cls) -> ClientBoardState:
        """Create a fresh 5-column board with no cards."""
        columns = [
            KanbanColumn(id=f"col-{idx + 1}", title=title, position=idx, card_ids=[])
            for idx, title in enumerate(DEFAULT_COLUMN_TITLES)
        ]
        return ClientBoardState(columns=columns, cards={})

    @classmethod
    def refresh_reset(
        cls, _state: Optional[ClientBoardState] = None
    ) -> ClientBoardState:
        """Stateless browser-refresh reset: discard transient state and return default board."""
        return cls.create_initial_board()

    @classmethod
    def add_card(
        cls,
        state: ClientBoardState,
        column_id: str,
        title: str,
        description: str = "",
        card_id: Optional[str] = None,
    ) -> ClientBoardState:
        """Create a card in the specified column with contiguous zero-indexed position."""
        next_state = state.model_copy(deep=True)
        col = cls._get_column(next_state, column_id)
        cid = card_id.strip() if card_id else f"card-{uuid4().hex[:8]}"
        if cid in next_state.cards:
            raise ValueError(f"Duplicate card id: {cid}")

        card = KanbanCard(
            id=cid,
            title=title,
            description=description,
            column_id=col.id,
            position=len(col.card_ids),
        )
        next_state.cards[cid] = card
        col.card_ids.append(cid)
        cls._reindex_column(next_state, col)
        cls.verify_invariants(next_state)
        return next_state

    @classmethod
    def move_card(
        cls,
        state: ClientBoardState,
        card_id: str,
        target_column_id: str,
        target_position: Optional[int] = None,
    ) -> ClientBoardState:
        """Move a card via drag-and-drop to a target column and zero-indexed position."""
        next_state = state.model_copy(deep=True)
        if card_id not in next_state.cards:
            raise KeyError(f"Unknown card id: {card_id}")

        card = next_state.cards[card_id]
        source_col = cls._get_column(next_state, card.column_id)
        target_col = cls._get_column(next_state, target_column_id)

        if card_id in source_col.card_ids:
            source_col.card_ids.remove(card_id)

        insert_at = (
            len(target_col.card_ids)
            if target_position is None
            else max(0, min(target_position, len(target_col.card_ids)))
        )
        target_col.card_ids.insert(insert_at, card_id)
        card.column_id = target_col.id

        cls._reindex_column(next_state, source_col)
        if target_col.id != source_col.id:
            cls._reindex_column(next_state, target_col)

        cls.verify_invariants(next_state)
        return next_state

    @classmethod
    def keyboard_move_card(
        cls,
        state: ClientBoardState,
        card_id: str,
        direction: KeyboardDirection,
    ) -> ClientBoardState:
        """Move a card using accessible keyboard navigation (up, down, left, right)."""
        if card_id not in state.cards:
            raise KeyError(f"Unknown card id: {card_id}")

        card = state.cards[card_id]
        source_col = cls._get_column(state, card.column_id)
        current_pos = source_col.card_ids.index(card_id)

        if direction == "up":
            return cls.move_card(state, card_id, source_col.id, max(0, current_pos - 1))
        if direction == "down":
            return cls.move_card(
                state,
                card_id,
                source_col.id,
                min(len(source_col.card_ids) - 1, current_pos + 1),
            )
        if direction == "left":
            new_col_idx = max(0, source_col.position - 1)
            target_col = sorted(state.columns, key=lambda c: c.position)[new_col_idx]
            if target_col.id == source_col.id:
                return state.model_copy(deep=True)
            return cls.move_card(state, card_id, target_col.id, current_pos)
        if direction == "right":
            new_col_idx = min(COLUMN_COUNT - 1, source_col.position + 1)
            target_col = sorted(state.columns, key=lambda c: c.position)[new_col_idx]
            if target_col.id == source_col.id:
                return state.model_copy(deep=True)
            return cls.move_card(state, card_id, target_col.id, current_pos)

        raise ValueError(f"Unsupported keyboard direction: {direction}")

    @classmethod
    def delete_card(cls, state: ClientBoardState, card_id: str) -> ClientBoardState:
        """Delete a card cleanly, removing its ID from all column lists with no orphans."""
        next_state = state.model_copy(deep=True)
        if card_id not in next_state.cards:
            raise KeyError(f"Unknown card id: {card_id}")

        del next_state.cards[card_id]
        for col in next_state.columns:
            if card_id in col.card_ids:
                col.card_ids = [cid for cid in col.card_ids if cid != card_id]
                cls._reindex_column(next_state, col)

        cls.verify_invariants(next_state)
        return next_state

    @classmethod
    def rename_column(
        cls, state: ClientBoardState, column_id: str, new_title: str
    ) -> ClientBoardState:
        """Rename a column while rejecting empty or whitespace-only titles."""
        cleaned = new_title.strip()
        if not cleaned:
            raise ValueError("Column title must be non-empty.")

        next_state = state.model_copy(deep=True)
        col = cls._get_column(next_state, column_id)
        col.title = cleaned
        cls.verify_invariants(next_state)
        return next_state

    @classmethod
    def verify_invariants(cls, state: ClientBoardState) -> None:
        """Assert fixed 5-column invariant, contiguous positions, and orphan-free state."""
        if len(state.columns) != COLUMN_COUNT:
            raise ValueError(f"Expected {COLUMN_COUNT} columns, got {len(state.columns)}.")

        seen_card_ids: set[str] = set()
        for col in state.columns:
            for idx, cid in enumerate(col.card_ids):
                if cid not in state.cards:
                    raise ValueError(f"Orphan card id {cid!r} in column {col.id!r}.")
                if cid in seen_card_ids:
                    raise ValueError(f"Duplicate card id {cid!r} across columns.")
                seen_card_ids.add(cid)
                card = state.cards[cid]
                if card.column_id != col.id or card.position != idx:
                    raise ValueError(
                        f"Card {cid!r} out of sync: expected ({col.id}, {idx}), "
                        f"got ({card.column_id}, {card.position})."
                    )

        if seen_card_ids != set(state.cards.keys()):
            raise ValueError("Board cards dict does not match column card_ids.")

    @staticmethod
    def _get_column(state: ClientBoardState, column_id: str) -> KanbanColumn:
        for col in state.columns:
            if col.id == column_id:
                return col
        raise KeyError(f"Unknown column id: {column_id}")

    @staticmethod
    def _reindex_column(state: ClientBoardState, col: KanbanColumn) -> None:
        for idx, cid in enumerate(col.card_ids):
            state.cards[cid].column_id = col.id
            state.cards[cid].position = idx
