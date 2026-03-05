"""FastAPI entrypoint for laser nesting planner."""

from __future__ import annotations

import logging
from pathlib import Path

from fastapi import FastAPI, HTTPException
from fastapi.responses import FileResponse, Response

from .export.dxf_exporter import export_plan_to_dxf
from .geometry import circle_area_mm2, circle_circumference_mm, effective_diameter_mm, sheet_area_mm2
from .nesting import compare_methods
from .nesting.grid import generate_grid
from .nesting.hexagonal import generate_hexagonal
from .schemas import Piece, PlanRequest, PlanResponse
from .utils import estimate_rows_and_cols, limit_quantity, validate_capacity_or_raise

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("laser-nesting")

app = FastAPI(title="Laser Nesting 3015F API", version="1.0.0")


def _build_svg(params: PlanRequest, pieces: list[Piece], title: str) -> str:
    grid_minor = "".join(
        f'<line x1="{x}" y1="0" x2="{x}" y2="{params.altura_chapa}" class="grid-minor" />'
        for x in range(0, int(params.largura_chapa) + 1, 100)
    ) + "".join(
        f'<line x1="0" y1="{y}" x2="{params.largura_chapa}" y2="{y}" class="grid-minor" />'
        for y in range(0, int(params.altura_chapa) + 1, 100)
    )
    grid_major = "".join(
        f'<line x1="{x}" y1="0" x2="{x}" y2="{params.altura_chapa}" class="grid-major" />'
        for x in range(0, int(params.largura_chapa) + 1, 500)
    ) + "".join(
        f'<line x1="0" y1="{y}" x2="{params.largura_chapa}" y2="{y}" class="grid-major" />'
        for y in range(0, int(params.altura_chapa) + 1, 500)
    )
    circles = "".join(
        f'<g><circle cx="{p.x}" cy="{p.y}" r="{p.raio}" class="piece" />'
        f'<text x="{p.x}" y="{p.y}" class="piece-id">{p.id}</text></g>'
        for p in pieces
    )
    return f"""<svg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 {params.largura_chapa} {params.altura_chapa}' width='{params.largura_chapa}' height='{params.altura_chapa}'>
<style>
.grid-minor{{stroke:#d7d9dc;stroke-width:0.8}} .grid-major{{stroke:#a5abb3;stroke-width:1.4}}
.piece{{fill:#f2f4f6;stroke:#333;stroke-width:1.2}} .piece-id{{font:10px sans-serif;text-anchor:middle;dominant-baseline:middle;fill:#111}}
</style>
<rect x='0' y='0' width='{params.largura_chapa}' height='{params.altura_chapa}' fill='#fff' stroke='#222' stroke-width='3'/>
{grid_minor}{grid_major}{circles}
<text x='10' y='20' font-size='18' fill='#111'>{title}</text>
</svg>"""


def _build_plan(params: PlanRequest) -> PlanResponse:
    d_eff = effective_diameter_mm(params.diametro_peca, params.kerf_laser, params.spacing)

    if params.metodo_preferido == "grid":
        pieces, step_y = generate_grid(params, d_eff)
        method = "grid"
    elif params.metodo_preferido == "hex":
        pieces, step_y = generate_hexagonal(params, d_eff)
        method = "hex"
    else:
        best = compare_methods(params)
        pieces, step_y, method = best.pieces, best.step_y, best.method

    pieces = limit_quantity(pieces, params.quantidade_desejada)
    validate_capacity_or_raise(params, pieces)

    total = len(pieces)
    area_sheet = sheet_area_mm2(params.largura_chapa, params.altura_chapa)
    area_pieces = total * circle_area_mm2(params.diametro_peca)
    utilization = (area_pieces / area_sheet) * 100.0 if area_sheet > 0 else 0.0

    cut_total = total * circle_circumference_mm(params.diametro_peca)
    tempo = cut_total / params.velocidade_corte
    rows, cols = estimate_rows_and_cols(pieces, step_y)
    title = f"Plano de corte - {total} peças Ø{params.diametro_peca:.0f} mm em chapa {params.largura_chapa:.0f}x{params.altura_chapa:.0f} mm"

    return PlanResponse(
        parametros_entrada=params,
        metodo_escolhido=method,
        diametro_efetivo=d_eff,
        pecas=pieces,
        total_pecas=total,
        linhas=rows,
        colunas_estimadas=cols,
        area_chapa=area_sheet,
        area_total_pecas=area_pieces,
        aproveitamento=utilization,
        comprimento_corte_total=cut_total,
        tempo_estimado=tempo,
        svg_inline=_build_svg(params, pieces, title),
    )


@app.post("/api/v1/plan", response_model=PlanResponse)
def create_plan(params: PlanRequest) -> PlanResponse:
    try:
        return _build_plan(params)
    except ValueError as exc:
        logger.error("Validation error: %s", exc)
        raise HTTPException(status_code=400, detail=str(exc)) from exc


@app.get("/api/v1/plan/dxf")
def export_dxf(
    largura_chapa: float = 3000,
    altura_chapa: float = 1500,
    espessura: float = 3,
    margem_borda: float = 10,
    diametro_peca: float = 127,
    kerf_laser: float = 1.5,
    spacing: float = 2,
    velocidade_corte: float = 35,
    metodo_preferido: str = "auto",
) -> FileResponse:
    params = PlanRequest(
        largura_chapa=largura_chapa,
        altura_chapa=altura_chapa,
        espessura=espessura,
        margem_borda=margem_borda,
        diametro_peca=diametro_peca,
        kerf_laser=kerf_laser,
        spacing=spacing,
        velocidade_corte=velocidade_corte,
        metodo_preferido=metodo_preferido,
    )
    plan = _build_plan(params)
    out = Path("/tmp/plano_nesting.dxf")
    export_plan_to_dxf(params, plan.pecas, out)
    return FileResponse(path=out, filename="plano_nesting.dxf", media_type="application/dxf")


@app.post("/api/v1/visual")
def render_visual(params: PlanRequest) -> Response:
    plan = _build_plan(params)
    return Response(content=plan.svg_inline or "", media_type="image/svg+xml")
