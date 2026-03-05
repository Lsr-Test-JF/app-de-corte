from app.geometry import effective_diameter_mm
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
        diametro_peca=127,
        kerf_laser=1.5,
        spacing=2,
        velocidade_corte=35,
    )


def test_known_case_counts_consistent() -> None:
    params = _base_params()
    d_eff = effective_diameter_mm(params.diametro_peca, params.kerf_laser, params.spacing)
    grid_pieces, _ = generate_grid(params, d_eff)
    hex_pieces, _ = generate_hexagonal(params, d_eff)
    assert len(grid_pieces) == 242
    assert len(hex_pieces) == 264


def test_compare_methods_prefers_hex() -> None:
    best = compare_methods(_base_params())
    assert best.method == "hex"
    assert len(best.pieces) == 264
