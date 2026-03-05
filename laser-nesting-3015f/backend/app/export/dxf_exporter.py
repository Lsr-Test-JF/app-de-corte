"""DXF export support using ezdxf."""

from __future__ import annotations

from pathlib import Path

import ezdxf

from ..schemas import Piece, PlanRequest


def export_plan_to_dxf(params: PlanRequest, pieces: list[Piece], file_path: str | Path) -> Path:
    """Export nesting plan to DXF with circles in mm."""
    target = Path(file_path)
    doc = ezdxf.new("R2010")
    doc.units = ezdxf.units.MM
    msp = doc.modelspace()

    for piece in pieces:
        msp.add_circle((piece.x, piece.y), params.diametro_peca / 2.0)

    metadata = [
        f"machine=3015F 3kW",
        f"sheet={params.largura_chapa}x{params.altura_chapa}mm",
        f"diam={params.diametro_peca}mm",
        f"kerf={params.kerf_laser}mm",
        f"spacing={params.spacing}mm",
    ]
    msp.add_mtext("\n".join(metadata), dxfattribs={"char_height": 12, "insert": (10, 10)})
    doc.saveas(target)
    return target
