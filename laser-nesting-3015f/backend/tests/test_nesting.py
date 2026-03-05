from app.geometry import effective_diameter_mm, shape_envelope_diameter_mm
from app.nesting import compare_methods
from app.nesting.grid import generate_grid
from app.nesting.hexagonal import generate_hexagonal
from app.schemas import PlanRequest


def _base_params() -> PlanRequest:
    return PlanRequest(
        largura_chapa=3000,
        altura_chapa=1500,
        espessura=3,
        margem_borda=10,
        formato='circulo',
        diametro_peca=127,
        kerf_laser=1.5,
        spacing=2,
        velocidade_corte=35,
    )


def test_known_case_counts_consistent() -> None:
    params = _base_params()
    d_eff = effective_diameter_mm(shape_envelope_diameter_mm(params), params.kerf_laser, params.spacing)
    grid_pieces, _ = generate_grid(params, d_eff)
    hex_pieces, _ = generate_hexagonal(params, d_eff)
    assert len(grid_pieces) > 0
    assert len(hex_pieces) >= len(grid_pieces)


def test_compare_methods_prefers_hex_or_grid() -> None:
    best = compare_methods(_base_params())
    assert best.method in {'hex', 'grid'}
    assert len(best.pieces) > 0
