"""Hexagonal nesting implementation."""

from __future__ import annotations

import math

from ..geometry import shape_envelope_diameter_mm
from ..schemas import Piece, PlanRequest
from ..utils import is_piece_inside_sheet


def generate_hexagonal(params: PlanRequest, effective_diameter: float) -> tuple[list[Piece], float]:
    envelope_radius = shape_envelope_diameter_mm(params) / 2.0
    step_x = effective_diameter
    step_y = effective_diameter * math.sqrt(3) / 2.0
    pieces: list[Piece] = []
    idx = 1
    row = 0

    y = params.margem_borda + envelope_radius
    while y <= params.altura_chapa - params.margem_borda - envelope_radius + 1e-9:
        shift = (effective_diameter / 2.0) if row % 2 == 1 else 0.0
        x = params.margem_borda + envelope_radius + shift
        while x <= params.largura_chapa - params.margem_borda - envelope_radius + 1e-9:
            if is_piece_inside_sheet(
                x,
                y,
                envelope_radius,
                params.largura_chapa,
                params.altura_chapa,
                params.margem_borda,
            ):
                pieces.append(Piece(id=idx, x=round(x, 4), y=round(y, 4), raio=round(envelope_radius, 4)))
                idx += 1
            x += step_x
        row += 1
        y += step_y
    return pieces, step_y
