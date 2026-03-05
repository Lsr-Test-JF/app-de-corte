"""DXF export support using ezdxf."""

from __future__ import annotations

from pathlib import Path

import ezdxf

from ..schemas import Piece, PlanRequest


def _polygon_offset(points: list[tuple[float, float]], cx: float, cy: float) -> list[tuple[float, float]]:
    xs = [p[0] for p in points]
    ys = [p[1] for p in points]
    min_x, max_x = min(xs), max(xs)
    min_y, max_y = min(ys), max(ys)
    ox = cx - (min_x + max_x) / 2.0
    oy = cy - (min_y + max_y) / 2.0
    return [(x + ox, y + oy) for x, y in points]


def export_plan_to_dxf(params: PlanRequest, pieces: list[Piece], file_path: str | Path) -> Path:
    target = Path(file_path)
    doc = ezdxf.new("R2010")
    doc.units = ezdxf.units.MM
    msp = doc.modelspace()

    for piece in pieces:
        if params.formato == "circulo":
            msp.add_circle((piece.x, piece.y), float(params.diametro_peca or 0) / 2.0)
        elif params.formato == "retangulo":
            w = float(params.largura_peca or 0)
            h = float(params.altura_peca or 0)
            x0, y0 = piece.x - w / 2.0, piece.y - h / 2.0
            msp.add_lwpolyline([(x0, y0), (x0 + w, y0), (x0 + w, y0 + h), (x0, y0 + h)], close=True)
        else:
            base = [(p.x, p.y) for p in (params.poligono_pontos or [])]
            pts = _polygon_offset(base, piece.x, piece.y)
            msp.add_lwpolyline(pts, close=True)

    metadata = [
        "machine=3015F 3kW",
        f"sheet={params.largura_chapa}x{params.altura_chapa}mm",
        f"formato={params.formato}",
        f"kerf={params.kerf_laser}mm",
        f"spacing={params.spacing}mm",
    ]
    msp.add_mtext("\n".join(metadata), dxfattribs={"char_height": 12, "insert": (10, 10)})
    doc.saveas(target)
    return target
