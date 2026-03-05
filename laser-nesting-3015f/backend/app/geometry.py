"""Pure geometry helpers for nesting calculations."""

from __future__ import annotations

import math


def effective_diameter_mm(diametro_peca: float, kerf_laser: float, spacing: float) -> float:
    """Calculate effective placement diameter in mm."""
    return diametro_peca + kerf_laser + spacing


def circle_area_mm2(diameter_mm: float) -> float:
    """Return area for a circle using diameter in mm."""
    radius = diameter_mm / 2.0
    return math.pi * radius * radius


def circle_circumference_mm(diameter_mm: float) -> float:
    """Return circumference for a circle using diameter in mm."""
    return math.pi * diameter_mm


def sheet_area_mm2(width_mm: float, height_mm: float) -> float:
    """Return rectangular sheet area in mm²."""
    return width_mm * height_mm
