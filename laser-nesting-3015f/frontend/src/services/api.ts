import { createDxfLocal, createPlanLocal } from './localEngine';

export type Point = { x: number; y: number };

export type PlanParams = {
  largura_chapa: number;
  altura_chapa: number;
  espessura: number;
  margem_borda: number;
  formato: 'circulo' | 'retangulo' | 'poligono';
  diametro_peca?: number;
  largura_peca?: number;
  altura_peca?: number;
  poligono_pontos?: Point[];
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
  parametros_entrada: Record<string, unknown>;
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

const BASE_URL = (import.meta.env.VITE_API_URL ?? '').trim();

export async function createPlan(params: PlanParams): Promise<PlanResult> {
  if (!BASE_URL) return createPlanLocal(params);

  try {
    const response = await fetch(`${BASE_URL}/api/v1/plan`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(params)
    });

    if (!response.ok) {
      const err = await response.json().catch(() => ({}));
      throw new Error(err.detail ?? 'Falha ao gerar plano');
    }

    return response.json();
  } catch {
    return createPlanLocal(params);
  }
}

export async function exportDxf(params: PlanParams, result: PlanResult): Promise<void> {
  if (BASE_URL) {
    try {
      const response = await fetch(`${BASE_URL}/api/v1/plan/dxf`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(params)
      });
      if (response.ok) {
        const blob = await response.blob();
        downloadBlob(blob, 'plano_nesting.dxf');
        return;
      }
    } catch {
      // fallback local
    }
  }

  const dxfContent = createDxfLocal(params, result.pecas);
  downloadBlob(new Blob([dxfContent], { type: 'application/dxf' }), 'plano_nesting_local.dxf');
}

function downloadBlob(blob: Blob, filename: string): void {
  const url = URL.createObjectURL(blob);
  const a = document.createElement('a');
  a.href = url;
  a.download = filename;
  a.click();
  URL.revokeObjectURL(url);
}
