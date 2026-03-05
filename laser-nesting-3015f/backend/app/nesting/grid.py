"""Grid nesting implementation."""

from __future__ import annotations

from ..schemas import Piece, PlanRequest
from ..utils import is_piece_inside_sheet


def generate_grid(params: PlanRequest, effective_diameter: float) -> tuple[list[Piece], float]:
    """Generate piece centers in a regular grid using effective spacing."""
    radius = params.diametro_peca / 2.0
    step = effective_diameter
    pieces: list[Piece] = []
    idx = 1

    y = params.margem_borda + radius
    while y <= params.altura_chapa - params.margem_borda - radius + 1e-9:
        x = params.margem_borda + radius
        while x <= params.largura_chapa - params.margem_borda - radius + 1e-9:
            if is_piece_inside_sheet(x, y, radius, params.largura_chapa, params.altura_chapa, params.margem_borda):
                pieces.append(Piece(id=idx, x=round(x, 4), y=round(y, 4), raio=radius))
                idx += 1
            x += step
        y += step
    return pieces, step
