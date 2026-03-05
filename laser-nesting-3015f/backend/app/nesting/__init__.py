"""Nesting strategy orchestrator."""

from __future__ import annotations

from dataclasses import dataclass

from ..geometry import circle_circumference_mm, effective_diameter_mm
from ..schemas import Piece, PlanRequest
from .grid import generate_grid
from .hexagonal import generate_hexagonal


@dataclass
class NestingResult:
    method: str
    pieces: list[Piece]
    step_y: float


def _cut_length_for_count(count: int, diametro_peca: float) -> float:
    return count * circle_circumference_mm(diametro_peca)


def compare_methods(params: PlanRequest) -> NestingResult:
    """Run grid and hexagonal methods and return the best result."""
    d_eff = effective_diameter_mm(params.diametro_peca, params.kerf_laser, params.spacing)
    grid_pieces, grid_step_y = generate_grid(params, d_eff)
    hex_pieces, hex_step_y = generate_hexagonal(params, d_eff)

    results = [
        NestingResult("grid", grid_pieces, grid_step_y),
        NestingResult("hex", hex_pieces, hex_step_y),
    ]

    results.sort(
        key=lambda r: (
            len(r.pieces),
            -_cut_length_for_count(len(r.pieces), params.diametro_peca),
        ),
        reverse=True,
    )
    return results[0]
