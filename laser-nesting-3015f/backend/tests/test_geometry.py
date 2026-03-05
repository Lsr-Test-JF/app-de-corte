import math

from app.geometry import circle_area_mm2, circle_circumference_mm, effective_diameter_mm


def test_effective_diameter() -> None:
    assert effective_diameter_mm(127, 1.5, 2) == 130.5


def test_circle_values() -> None:
    assert math.isclose(circle_circumference_mm(100), math.pi * 100)
    assert math.isclose(circle_area_mm2(100), math.pi * 50 * 50)
