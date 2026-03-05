from pathlib import Path

import ezdxf

from app.export.dxf_exporter import export_plan_to_dxf
from app.geometry import effective_diameter_mm
from app.nesting.hexagonal import generate_hexagonal
from app.schemas import PlanRequest


def test_dxf_export_contains_circles(tmp_path: Path) -> None:
    params = PlanRequest(
        largura_chapa=1000,
        altura_chapa=1000,
        espessura=3,
        margem_borda=10,
        diametro_peca=100,
        kerf_laser=1.5,
        spacing=2,
        velocidade_corte=30,
    )
    d_eff = effective_diameter_mm(params.diametro_peca, params.kerf_laser, params.spacing)
    pieces, _ = generate_hexagonal(params, d_eff)
    pieces = pieces[:10]
    output = tmp_path / "test_plan.dxf"

    export_plan_to_dxf(params, pieces, output)

    assert output.exists()
    doc = ezdxf.readfile(output)
    circles = [e for e in doc.modelspace() if e.dxftype() == "CIRCLE"]
    assert len(circles) == 10
