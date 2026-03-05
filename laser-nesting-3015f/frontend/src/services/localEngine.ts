import { PlanParams, PlanResult, Piece } from './api';

const round4 = (v: number) => Math.round(v * 10000) / 10000;

function inside(x: number, y: number, r: number, p: PlanParams): boolean {
  return (
    x - r >= p.margem_borda &&
    x + r <= p.largura_chapa - p.margem_borda &&
    y - r >= p.margem_borda &&
    y + r <= p.altura_chapa - p.margem_borda
  );
}

function gridPieces(p: PlanParams, dEff: number): Piece[] {
  const r = p.diametro_peca / 2;
  const out: Piece[] = [];
  let id = 1;
  for (let y = p.margem_borda + r; y <= p.altura_chapa - p.margem_borda - r + 1e-9; y += dEff) {
    for (let x = p.margem_borda + r; x <= p.largura_chapa - p.margem_borda - r + 1e-9; x += dEff) {
      if (inside(x, y, r, p)) out.push({ id: id++, x: round4(x), y: round4(y), raio: r });
    }
  }
  return out;
}

function hexPieces(p: PlanParams, dEff: number): Piece[] {
  const r = p.diametro_peca / 2;
  const stepY = (dEff * Math.sqrt(3)) / 2;
  const out: Piece[] = [];
  let id = 1;
  let row = 0;

  for (let y = p.margem_borda + r; y <= p.altura_chapa - p.margem_borda - r + 1e-9; y += stepY) {
    const shift = row % 2 ? dEff / 2 : 0;
    for (let x = p.margem_borda + r + shift; x <= p.largura_chapa - p.margem_borda - r + 1e-9; x += dEff) {
      if (inside(x, y, r, p)) out.push({ id: id++, x: round4(x), y: round4(y), raio: r });
    }
    row += 1;
  }
  return out;
}

function estimateRowsCols(pieces: Piece[]): { linhas: number; colunas_estimadas: number } {
  const grouped = new Map<string, number>();
  for (const piece of pieces) {
    const key = piece.y.toFixed(2);
    grouped.set(key, (grouped.get(key) ?? 0) + 1);
  }
  const linhas = grouped.size;
  let colunas_estimadas = 0;
  grouped.forEach((c) => {
    if (c > colunas_estimadas) colunas_estimadas = c;
  });
  return { linhas, colunas_estimadas };
}

function buildSvg(p: PlanParams, pieces: Piece[]): string {
  const circles = pieces
    .map(
      (piece) =>
        `<g><circle cx='${piece.x}' cy='${piece.y}' r='${piece.raio}' class='piece'/><text x='${piece.x}' y='${piece.y}' class='piece-id'>${piece.id}</text></g>`
    )
    .join('');
  return `<svg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 ${p.largura_chapa} ${p.altura_chapa}' width='${p.largura_chapa}' height='${p.altura_chapa}'>
<style>.piece{fill:#f2f4f6;stroke:#111827;stroke-width:1}.piece-id{font:10px sans-serif;text-anchor:middle;dominant-baseline:middle;fill:#111}</style>
<rect x='0' y='0' width='${p.largura_chapa}' height='${p.altura_chapa}' fill='white' stroke='#1f2937' stroke-width='4'/>
${circles}</svg>`;
}

export function createPlanLocal(params: PlanParams): PlanResult {
  const dEff = params.diametro_peca + params.kerf_laser + params.spacing;
  const grid = gridPieces(params, dEff);
  const hex = hexPieces(params, dEff);

  let method = params.metodo_preferido;
  if (method === 'auto') method = hex.length >= grid.length ? 'hex' : 'grid';

  const selected = method === 'grid' ? grid : hex;
  const pieces = params.quantidade_desejada ? selected.slice(0, params.quantidade_desejada) : selected;
  if (!pieces.length) throw new Error('Peça não cabe na chapa com os parâmetros atuais.');

  const areaChapa = params.largura_chapa * params.altura_chapa;
  const areaPeca = Math.PI * (params.diametro_peca / 2) ** 2;
  const areaTotalPecas = areaPeca * pieces.length;
  const comprimento = pieces.length * Math.PI * params.diametro_peca;
  const tempo = comprimento / params.velocidade_corte;
  const { linhas, colunas_estimadas } = estimateRowsCols(pieces);

  return {
    metodo_escolhido: method,
    total_pecas: pieces.length,
    linhas,
    colunas_estimadas,
    diametro_efetivo: dEff,
    aproveitamento: (areaTotalPecas / areaChapa) * 100,
    comprimento_corte_total: comprimento,
    tempo_estimado: tempo,
    pecas: pieces,
    area_chapa: areaChapa,
    area_total_pecas: areaTotalPecas,
    svg_inline: buildSvg(params, pieces)
  };
}

export function createDxfLocal(params: PlanParams, pieces: Piece[]): string {
  const lines: string[] = ['0', 'SECTION', '2', 'ENTITIES'];
  for (const piece of pieces) {
    lines.push('0', 'CIRCLE', '8', '0', '10', `${piece.x}`, '20', `${piece.y}`, '30', '0.0', '40', `${params.diametro_peca / 2}`);
  }
  lines.push('0', 'ENDSEC', '0', 'EOF');
  return lines.join('\n');
}
