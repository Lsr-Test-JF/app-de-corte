import math

from app.geometry import effective_diameter_mm, piece_area_mm2, piece_perimeter_mm, shape_envelope_diameter_mm
from app.schemas import PlanRequest


def test_effective_diameter() -> None:
    assert effective_diameter_mm(127, 1.5, 2) == 130.5


def test_circle_values() -> None:
    params = PlanRequest(formato='circulo', diametro_peca=100)
    assert math.isclose(piece_perimeter_mm(params), math.pi * 100)
    assert math.isclose(piece_area_mm2(params), math.pi * 50 * 50)


def test_rectangle_envelope() -> None:
    params = PlanRequest(formato='retangulo', largura_peca=120, altura_peca=80, diametro_peca=None)
    assert math.isclose(shape_envelope_diameter_mm(params), math.hypot(120, 80))
