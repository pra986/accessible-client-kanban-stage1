"""Pydantic v2 data models for the Stage-1 client-side Kanban board."""

from __future__ import annotations

from typing import Dict, List

from pydantic import BaseModel, Field, field_validator

COLUMN_COUNT = 5
DEFAULT_COLUMN_TITLES: tuple[str, ...] = (
    "Backlog",
    "To Do",
    "In Progress",
    "Review",
    "Done",
)


class KanbanCard(BaseModel):
    """Represents a single Kanban card inside a column."""

    id: str
    title: str
    description: str = ""
    column_id: str
    position: int = Field(default=0, ge=0)

    @field_validator("id", "column_id")
    @classmethod
    def _validate_non_empty_id(cls, value: str) -> str:
        cleaned = value.strip()
        if not cleaned:
            raise ValueError("Identifier must be non-empty.")
        return cleaned

    @field_validator("title")
    @classmethod
    def _validate_title(cls, value: str) -> str:
        cleaned = value.strip()
        if not cleaned:
            raise ValueError("Card title must be non-empty.")
        return cleaned


class KanbanColumn(BaseModel):
    """Represents one of the 5 fixed columns on the Kanban board."""

    id: str
    title: str
    position: int = Field(ge=0, lt=COLUMN_COUNT)
    card_ids: List[str] = Field(default_factory=list)

    @field_validator("id")
    @classmethod
    def _validate_id(cls, value: str) -> str:
        cleaned = value.strip()
        if not cleaned:
            raise ValueError("Column id must be non-empty.")
        return cleaned

    @field_validator("title")
    @classmethod
    def _validate_title(cls, value: str) -> str:
        cleaned = value.strip()
        if not cleaned:
            raise ValueError("Column title must be non-empty.")
        return cleaned


class ClientBoardState(BaseModel):
    """Complete client-side state of the Stage-1 Kanban board."""

    columns: List[KanbanColumn]
    cards: Dict[str, KanbanCard] = Field(default_factory=dict)

    @field_validator("columns")
    @classmethod
    def _validate_five_columns(cls, value: List[KanbanColumn]) -> List[KanbanColumn]:
        if len(value) != COLUMN_COUNT:
            raise ValueError(
                f"Board must have exactly {COLUMN_COUNT} columns; got {len(value)}."
            )
        return value
