import { PlanParams, PlanResult, Piece } from './api';

const round4 = (v: number) => Math.round(v * 10000) / 10000;

function shapeDiameter(p: PlanParams): number {
  if (p.formato === 'circulo') return p.diametro_peca || 0;
  if (p.formato === 'retangulo') return Math.hypot(p.largura_peca || 0, p.altura_peca || 0);
  const pts = p.poligono_pontos || [];
  const xs = pts.map((pt) => pt.x);
  const ys = pts.map((pt) => pt.y);
  return Math.hypot(Math.max(...xs) - Math.min(...xs), Math.max(...ys) - Math.min(...ys));
}

function pieceArea(p: PlanParams): number {
  if (p.formato === 'circulo') return Math.PI * ((p.diametro_peca || 0) / 2) ** 2;
  if (p.formato === 'retangulo') return (p.largura_peca || 0) * (p.altura_peca || 0);
  const pts = p.poligono_pontos || [];
  let area = 0;
  for (let i = 0; i < pts.length; i += 1) {
    const j = (i + 1) % pts.length;
    area += pts[i].x * pts[j].y - pts[j].x * pts[i].y;
  }
  return Math.abs(area) / 2;
}

function piecePerimeter(p: PlanParams): number {
  if (p.formato === 'circulo') return Math.PI * (p.diametro_peca || 0);
  if (p.formato === 'retangulo') return 2 * ((p.largura_peca || 0) + (p.altura_peca || 0));
  const pts = p.poligono_pontos || [];
  let per = 0;
  for (let i = 0; i < pts.length; i += 1) {
    const j = (i + 1) % pts.length;
    per += Math.hypot(pts[j].x - pts[i].x, pts[j].y - pts[i].y);
  }
  return per;
}

function inside(x: number, y: number, r: number, p: PlanParams): boolean {
  return x - r >= p.margem_borda && x + r <= p.largura_chapa - p.margem_borda && y - r >= p.margem_borda && y + r <= p.altura_chapa - p.margem_borda;
}

function gridPieces(p: PlanParams, dEff: number, r: number): Piece[] {
  const out: Piece[] = [];
  let id = 1;
  for (let y = p.margem_borda + r; y <= p.altura_chapa - p.margem_borda - r + 1e-9; y += dEff) {
    for (let x = p.margem_borda + r; x <= p.largura_chapa - p.margem_borda - r + 1e-9; x += dEff) {
      if (inside(x, y, r, p)) out.push({ id: id += 1, x: round4(x), y: round4(y), raio: round4(r) });
    }
  }
  return out.map((piece, idx) => ({ ...piece, id: idx + 1 }));
}

function hexPieces(p: PlanParams, dEff: number, r: number): Piece[] {
  const stepY = (dEff * Math.sqrt(3)) / 2;
  const out: Piece[] = [];
  let id = 1;
  let row = 0;
  for (let y = p.margem_borda + r; y <= p.altura_chapa - p.margem_borda - r + 1e-9; y += stepY) {
    const shift = row % 2 ? dEff / 2 : 0;
    for (let x = p.margem_borda + r + shift; x <= p.largura_chapa - p.margem_borda - r + 1e-9; x += dEff) {
      if (inside(x, y, r, p)) out.push({ id: id += 1, x: round4(x), y: round4(y), raio: round4(r) });
    }
    row += 1;
  }
  return out.map((piece, idx) => ({ ...piece, id: idx + 1 }));
}

function estimateRowsCols(pieces: Piece[]): { linhas: number; colunas_estimadas: number } {
  const grouped = new Map<string, number>();
  for (const piece of pieces) {
    const key = piece.y.toFixed(2);
    grouped.set(key, (grouped.get(key) ?? 0) + 1);
  }
  return { linhas: grouped.size, colunas_estimadas: Math.max(...Array.from(grouped.values()), 0) };
}

function buildSvg(p: PlanParams, pieces: Piece[]): string {
  const shapes = pieces
    .map((piece) => {
      if (p.formato === 'circulo') {
        const rr = (p.diametro_peca || 0) / 2;
        return `<g><circle cx='${piece.x}' cy='${piece.y}' r='${rr}' class='piece'/><text x='${piece.x}' y='${piece.y}' class='piece-id'>${piece.id}</text></g>`;
      }
      if (p.formato === 'retangulo') {
        const w = p.largura_peca || 0;
        const h = p.altura_peca || 0;
        return `<g><rect x='${piece.x - w / 2}' y='${piece.y - h / 2}' width='${w}' height='${h}' class='piece'/><text x='${piece.x}' y='${piece.y}' class='piece-id'>${piece.id}</text></g>`;
      }
      const pts = p.poligono_pontos || [];
      const xs = pts.map((pt) => pt.x);
      const ys = pts.map((pt) => pt.y);
      const cx = (Math.max(...xs) + Math.min(...xs)) / 2;
      const cy = (Math.max(...ys) + Math.min(...ys)) / 2;
      const d = pts.map((pt) => `${pt.x - cx + piece.x},${pt.y - cy + piece.y}`).join(' ');
      return `<g><polygon points='${d}' class='piece'/><text x='${piece.x}' y='${piece.y}' class='piece-id'>${piece.id}</text></g>`;
    })
    .join('');
  return `<svg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 ${p.largura_chapa} ${p.altura_chapa}' width='${p.largura_chapa}' height='${p.altura_chapa}'><style>.piece{fill:#f2f4f6;stroke:#111827;stroke-width:1}.piece-id{font:10px sans-serif;text-anchor:middle;dominant-baseline:middle;fill:#111}</style><rect x='0' y='0' width='${p.largura_chapa}' height='${p.altura_chapa}' fill='white' stroke='#1f2937' stroke-width='4'/>${shapes}</svg>`;
}

export function createPlanLocal(params: PlanParams): PlanResult {
  const diameter = shapeDiameter(params);
  const radius = diameter / 2;
  const dEff = diameter + params.kerf_laser + params.spacing;
  const grid = gridPieces(params, dEff, radius);
  const hex = hexPieces(params, dEff, radius);
  const method = params.metodo_preferido === 'auto' ? (hex.length >= grid.length ? 'hex' : 'grid') : params.metodo_preferido;
  const selected = method === 'grid' ? grid : hex;
  const pieces = params.quantidade_desejada ? selected.slice(0, params.quantidade_desejada) : selected;
  if (!pieces.length) throw new Error('Peça não cabe na chapa com os parâmetros atuais.');

  const areaChapa = params.largura_chapa * params.altura_chapa;
  const areaTotalPecas = pieceArea(params) * pieces.length;
  const comprimento = piecePerimeter(params) * pieces.length;
  const tempo = comprimento / params.velocidade_corte;
  const { linhas, colunas_estimadas } = estimateRowsCols(pieces);

  return {
    parametros_entrada: {
      'largura_chapa_(mm)': params.largura_chapa,
      'altura_chapa_(mm)': params.altura_chapa,
      'espessura_(mm)': params.espessura,
      'margem_borda_(mm)': params.margem_borda,
      formato: params.formato,
      'diametro_peca_(mm)': params.formato === 'circulo' ? params.diametro_peca : null,
      'largura_peca_(mm)': params.formato === 'retangulo' ? params.largura_peca : null,
      'altura_peca_(mm)': params.formato === 'retangulo' ? params.altura_peca : null,
      poligono_pontos: params.formato === 'poligono' ? params.poligono_pontos : null,
      'kerf_laser_(mm)': params.kerf_laser,
      'Espaçamento_entre_peças_(mm)': params.spacing,
      lead_in_mm: params.lead_in_mm,
      lead_out_mm: params.lead_out_mm,
      metodo_preferido: params.metodo_preferido
    },
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
    if (params.formato === 'circulo') {
      lines.push('0', 'CIRCLE', '8', '0', '10', `${piece.x}`, '20', `${piece.y}`, '30', '0.0', '40', `${(params.diametro_peca || 0) / 2}`);
    } else if (params.formato === 'retangulo') {
      const w = params.largura_peca || 0;
      const h = params.altura_peca || 0;
      const x0 = piece.x - w / 2;
      const y0 = piece.y - h / 2;
      lines.push('0', 'LWPOLYLINE', '8', '0', '90', '4', '70', '1', '10', `${x0}`, '20', `${y0}`, '10', `${x0 + w}`, '20', `${y0}`, '10', `${x0 + w}`, '20', `${y0 + h}`, '10', `${x0}`, '20', `${y0 + h}`);
    }
  }
  lines.push('0', 'ENDSEC', '0', 'EOF');
  return lines.join('\n');
}
