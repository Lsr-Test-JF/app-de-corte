"""Validation and helper utilities."""

from __future__ import annotations

import math
from typing import Iterable

from .schemas import Piece, PlanRequest


def is_piece_inside_sheet(
    x: float,
    y: float,
    radius: float,
    width: float,
    height: float,
    margin: float,
) -> bool:
    """Check if a piece remains fully inside the sheet useful area."""
    return (
        x - radius >= margin
        and x + radius <= width - margin
        and y - radius >= margin
        and y + radius <= height - margin
    )


def limit_quantity(pieces: list[Piece], quantity: int | None) -> list[Piece]:
    """Trim piece list to desired quantity if requested."""
    if quantity is None:
        return pieces
    return pieces[:quantity]


def estimate_rows_and_cols(pieces: Iterable[Piece], step_y: float, tol: float = 1e-3) -> tuple[int, int]:
    """Approximate number of rows and max columns from piece centers."""
    ys = sorted([p.y for p in pieces])
    if not ys:
        return 0, 0
    rows: list[float] = []
    for y in ys:
        if not rows or math.fabs(y - rows[-1]) > max(step_y * 0.25, tol):
            rows.append(y)
    row_count = len(rows)
    cols = 0
    for ry in rows:
        c = len([y for y in ys if math.fabs(y - ry) <= max(step_y * 0.25, tol)])
        cols = max(cols, c)
    return row_count, cols


def validate_capacity_or_raise(params: PlanRequest, pieces: list[Piece]) -> None:
    """Raise a ValueError when no piece could be positioned."""
    if not pieces:
        raise ValueError("Peça não cabe na chapa com os parâmetros atuais.")
