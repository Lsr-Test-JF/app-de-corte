"""Pure geometry helpers for nesting calculations."""

from __future__ import annotations

import math

from .schemas import PlanRequest


def shape_envelope_diameter_mm(params: PlanRequest) -> float:
    if params.formato == "circulo":
        return float(params.diametro_peca or 0)
    if params.formato == "retangulo":
        return math.hypot(float(params.largura_peca or 0), float(params.altura_peca or 0))

    xs = [p.x for p in (params.poligono_pontos or [])]
    ys = [p.y for p in (params.poligono_pontos or [])]
    width = max(xs) - min(xs)
    height = max(ys) - min(ys)
    return math.hypot(width, height)


def effective_diameter_mm(shape_diameter: float, kerf_laser: float, spacing: float) -> float:
    return shape_diameter + kerf_laser + spacing


def piece_area_mm2(params: PlanRequest) -> float:
    if params.formato == "circulo":
        radius = float(params.diametro_peca or 0) / 2.0
        return math.pi * radius * radius
    if params.formato == "retangulo":
        return float(params.largura_peca or 0) * float(params.altura_peca or 0)

    pts = params.poligono_pontos or []
    area = 0.0
    for i in range(len(pts)):
        j = (i + 1) % len(pts)
        area += pts[i].x * pts[j].y - pts[j].x * pts[i].y
    return abs(area) / 2.0


def piece_perimeter_mm(params: PlanRequest) -> float:
    if params.formato == "circulo":
        return math.pi * float(params.diametro_peca or 0)
    if params.formato == "retangulo":
        return 2.0 * (float(params.largura_peca or 0) + float(params.altura_peca or 0))

    pts = params.poligono_pontos or []
    perimeter = 0.0
    for i in range(len(pts)):
        j = (i + 1) % len(pts)
        perimeter += math.hypot(pts[j].x - pts[i].x, pts[j].y - pts[i].y)
    return perimeter


def sheet_area_mm2(width_mm: float, height_mm: float) -> float:
    return width_mm * height_mm
