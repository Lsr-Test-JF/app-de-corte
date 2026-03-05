"""Pydantic models for API payloads."""

from __future__ import annotations

from typing import Literal

from pydantic import BaseModel, Field, model_validator

from . import config


class PolygonPoint(BaseModel):
    x: float
    y: float


class PlanRequest(BaseModel):
    largura_chapa: float = Field(default=config.DEFAULT_SHEET_WIDTH_MM, gt=0)
    altura_chapa: float = Field(default=config.DEFAULT_SHEET_HEIGHT_MM, gt=0)
    espessura: float = Field(default=config.DEFAULT_THICKNESS_MM, gt=0)
    margem_borda: float = Field(default=config.DEFAULT_MARGIN_MM, ge=0)

    formato: Literal["circulo", "retangulo", "poligono"] = "circulo"
    diametro_peca: float | None = Field(default=config.DEFAULT_DIAMETER_MM, gt=0)
    largura_peca: float | None = Field(default=None, gt=0)
    altura_peca: float | None = Field(default=None, gt=0)
    poligono_pontos: list[PolygonPoint] | None = None

    kerf_laser: float = Field(default=config.DEFAULT_KERF_MM, ge=0)
    spacing: float = Field(default=config.DEFAULT_SPACING_MM, ge=0)
    quantidade_desejada: int | None = Field(default=None, gt=0)
    velocidade_corte: float = Field(default=config.DEFAULT_CUT_SPEED_MM_S, gt=0)
    lead_in_mm: float = Field(default=0.0, ge=0)
    lead_out_mm: float = Field(default=0.0, ge=0)
    metodo_preferido: Literal["auto", "grid", "hex"] = "auto"

    @model_validator(mode="after")
    def validate_shape(self) -> "PlanRequest":
        if self.largura_chapa <= 2 * self.margem_borda or self.altura_chapa <= 2 * self.margem_borda:
            raise ValueError("Margem de borda inviabiliza a área útil da chapa.")

        if self.formato == "circulo" and not self.diametro_peca:
            raise ValueError("Informe diametro_peca para formato circulo.")
        if self.formato == "retangulo" and (not self.largura_peca or not self.altura_peca):
            raise ValueError("Informe largura_peca e altura_peca para formato retangulo.")
        if self.formato == "poligono":
            if not self.poligono_pontos or len(self.poligono_pontos) < 3:
                raise ValueError("Informe ao menos 3 pontos para formato poligono.")
        return self


class Piece(BaseModel):
    id: int
    x: float
    y: float
    raio: float


class ParametrosEntradaNominais(BaseModel):
    largura_chapa_mm: float = Field(alias="largura_chapa_(mm)")
    altura_chapa_mm: float = Field(alias="altura_chapa_(mm)")
    espessura_mm: float = Field(alias="espessura_(mm)")
    margem_borda_mm: float = Field(alias="margem_borda_(mm)")
    formato: str
    diametro_peca_mm: float | None = Field(default=None, alias="diametro_peca_(mm)")
    largura_peca_mm: float | None = Field(default=None, alias="largura_peca_(mm)")
    altura_peca_mm: float | None = Field(default=None, alias="altura_peca_(mm)")
    poligono_pontos: list[PolygonPoint] | None = None
    kerf_laser_mm: float = Field(alias="kerf_laser_(mm)")
    espacamento_entre_pecas_mm: float = Field(alias="Espaçamento_entre_peças_(mm)")
    lead_in_mm: float
    lead_out_mm: float
    metodo_preferido: str


class PlanResponse(BaseModel):
    parametros_entrada: dict[str, object]
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
