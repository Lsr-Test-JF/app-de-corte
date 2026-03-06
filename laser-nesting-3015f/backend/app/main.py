"""FastAPI entrypoint for laser nesting planner."""

from __future__ import annotations

import logging
from pathlib import Path

from fastapi import FastAPI, HTTPException
from fastapi.responses import FileResponse, Response

from .export.dxf_exporter import export_plan_to_dxf
from .geometry import (
    effective_diameter_mm,
    piece_area_mm2,
    piece_perimeter_mm,
    shape_envelope_diameter_mm,
    sheet_area_mm2,
)
from .nesting import compare_methods
from .nesting.grid import generate_grid
from .nesting.hexagonal import generate_hexagonal
from .schemas import Piece, PlanRequest, PlanResponse
from .utils import estimate_rows_and_cols, limit_quantity, validate_capacity_or_raise

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("laser-nesting")

app = FastAPI(title="Laser Nesting 3015F API", version="1.1.0")


def _shape_svg(params: PlanRequest, piece: Piece) -> str:
    if params.formato == "circulo":
        real_r = float(params.diametro_peca or 0) / 2.0
        return f"<circle cx='{piece.x}' cy='{piece.y}' r='{real_r}' class='piece'/>"
    if params.formato == "retangulo":
        w = float(params.largura_peca or 0)
        h = float(params.altura_peca or 0)
        return f"<rect x='{piece.x - w/2}' y='{piece.y - h/2}' width='{w}' height='{h}' class='piece'/>"

    points = params.poligono_pontos or []
    xs = [p.x for p in points]
    ys = [p.y for p in points]
    cx = (max(xs) + min(xs)) / 2.0
    cy = (max(ys) + min(ys)) / 2.0
    pts = " ".join(f"{p.x - cx + piece.x},{p.y - cy + piece.y}" for p in points)
    return f"<polygon points='{pts}' class='piece'/>"


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
    shapes = "".join(
        f"<g>{_shape_svg(params, p)}<text x='{p.x}' y='{p.y}' class='piece-id'>{p.id}</text></g>" for p in pieces
    )

    return f"""<svg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 {params.largura_chapa} {params.altura_chapa}' width='{params.largura_chapa}' height='{params.altura_chapa}'>
<style>
.grid-minor{{stroke:#d7d9dc;stroke-width:0.8}} .grid-major{{stroke:#a5abb3;stroke-width:1.4}}
.piece{{fill:#f2f4f6;stroke:#333;stroke-width:1.2}} .piece-id{{font:10px sans-serif;text-anchor:middle;dominant-baseline:middle;fill:#111}}
</style>
<rect x='0' y='0' width='{params.largura_chapa}' height='{params.altura_chapa}' fill='#fff' stroke='#222' stroke-width='3'/>
{grid_minor}{grid_major}{shapes}
<text x='10' y='20' font-size='18' fill='#111'>{title}</text>
</svg>"""


def _parametros_entrada_nomeados(params: PlanRequest) -> dict[str, object]:
    return {
        "largura_chapa_(mm)": params.largura_chapa,
        "altura_chapa_(mm)": params.altura_chapa,
        "espessura_(mm)": params.espessura,
        "margem_borda_(mm)": params.margem_borda,
        "formato": params.formato,
        "diametro_peca_(mm)": params.diametro_peca if params.formato == "circulo" else None,
        "largura_peca_(mm)": params.largura_peca if params.formato == "retangulo" else None,
        "altura_peca_(mm)": params.altura_peca if params.formato == "retangulo" else None,
        "poligono_pontos": [p.model_dump() for p in (params.poligono_pontos or [])] if params.formato == "poligono" else None,
        "kerf_laser_(mm)": params.kerf_laser,
        "Espaçamento_entre_peças_(mm)": params.spacing,
        "lead_in_mm": params.lead_in_mm,
        "lead_out_mm": params.lead_out_mm,
        "metodo_preferido": params.metodo_preferido,
    }


def _build_plan(params: PlanRequest) -> PlanResponse:
    shape_d = shape_envelope_diameter_mm(params)
    d_eff = effective_diameter_mm(shape_d, params.kerf_laser, params.spacing)

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
    unit_area = piece_area_mm2(params)
    area_pieces = total * unit_area
    utilization = (area_pieces / area_sheet) * 100.0 if area_sheet > 0 else 0.0

    cut_total = total * piece_perimeter_mm(params)
    tempo = cut_total / params.velocidade_corte
    rows, cols = estimate_rows_and_cols(pieces, step_y)
    title = (
        f"Plano de corte - {total} peças {params.formato} em chapa "
        f"{params.largura_chapa:.0f}x{params.altura_chapa:.0f} mm"
    )

    return PlanResponse(
        parametros_entrada=_parametros_entrada_nomeados(params),
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


@app.post("/api/v1/plan/dxf")
def export_dxf_post(params: PlanRequest) -> FileResponse:
    plan = _build_plan(params)
    out = Path("/tmp/plano_nesting.dxf")
    export_plan_to_dxf(params, plan.pecas, out)
    return FileResponse(path=out, filename="plano_nesting.dxf", media_type="application/dxf")


@app.post("/api/v1/visual")
def render_visual(params: PlanRequest) -> Response:
    plan = _build_plan(params)
    return Response(content=plan.svg_inline or "", media_type="image/svg+xml")
