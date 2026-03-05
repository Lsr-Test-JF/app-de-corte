"""Pydantic models for API payloads."""

from __future__ import annotations

from typing import Literal

from pydantic import BaseModel, Field, model_validator

from . import config


class PlanRequest(BaseModel):
    largura_chapa: float = Field(default=config.DEFAULT_SHEET_WIDTH_MM, gt=0)
    altura_chapa: float = Field(default=config.DEFAULT_SHEET_HEIGHT_MM, gt=0)
    espessura: float = Field(default=config.DEFAULT_THICKNESS_MM, gt=0)
    margem_borda: float = Field(default=config.DEFAULT_MARGIN_MM, ge=0)
    diametro_peca: float = Field(default=config.DEFAULT_DIAMETER_MM, gt=0)
    kerf_laser: float = Field(default=config.DEFAULT_KERF_MM, ge=0)
    spacing: float = Field(default=config.DEFAULT_SPACING_MM, ge=0)
    quantidade_desejada: int | None = Field(default=None, gt=0)
    velocidade_corte: float = Field(default=config.DEFAULT_CUT_SPEED_MM_S, gt=0)
    lead_in_mm: float = Field(default=0.0, ge=0)
    lead_out_mm: float = Field(default=0.0, ge=0)
    metodo_preferido: Literal["auto", "grid", "hex"] = "auto"

    @model_validator(mode="after")
    def validate_sheet(self) -> "PlanRequest":
        if self.largura_chapa <= 2 * self.margem_borda or self.altura_chapa <= 2 * self.margem_borda:
            raise ValueError("Margem de borda inviabiliza a área útil da chapa.")
        return self


class Piece(BaseModel):
    id: int
    x: float
    y: float
    raio: float


class PlanResponse(BaseModel):
    parametros_entrada: PlanRequest
    metodo_escolhido: str
    diametro_efetivo: float
    pecas: list[Piece]
    total_pecas: int
    linhas: int
    colunas_estimadas: int
    area_chapa: float
    area_total_pecas: float
    aproveitamento: float
    comprimento_corte_total: float
    tempo_estimado: float
    svg_inline: str | None = None
