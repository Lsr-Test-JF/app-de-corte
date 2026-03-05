export type PlanParams = {
  largura_chapa: number;
  altura_chapa: number;
  espessura: number;
  margem_borda: number;
  diametro_peca: number;
  kerf_laser: number;
  spacing: number;
  quantidade_desejada?: number;
  velocidade_corte: number;
  lead_in_mm: number;
  lead_out_mm: number;
  metodo_preferido: 'auto' | 'grid' | 'hex';
};

export type Piece = { id: number; x: number; y: number; raio: number };

export type PlanResult = {
  metodo_escolhido: string;
  total_pecas: number;
  linhas: number;
  colunas_estimadas: number;
  diametro_efetivo: number;
  aproveitamento: number;
  comprimento_corte_total: number;
  tempo_estimado: number;
  pecas: Piece[];
  area_chapa: number;
  area_total_pecas: number;
  svg_inline?: string;
};

const BASE_URL = import.meta.env.VITE_API_URL ?? 'http://localhost:8000';

export async function createPlan(params: PlanParams): Promise<PlanResult> {
  const response = await fetch(`${BASE_URL}/api/v1/plan`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(params)
  });
  if (!response.ok) {
    const err = await response.json();
    throw new Error(err.detail ?? 'Falha ao gerar plano');
  }
  return response.json();
}

export function dxfUrl(params: PlanParams): string {
  const query = new URLSearchParams(params as unknown as Record<string, string>);
  return `${BASE_URL}/api/v1/plan/dxf?${query.toString()}`;
}
