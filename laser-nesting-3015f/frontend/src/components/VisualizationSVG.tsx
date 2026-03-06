import { useMemo, useState } from 'react';
import { PlanResult } from '../services/api';

type Props = { result: PlanResult | null; width: number; height: number };

export default function VisualizationSVG({ result, width, height }: Props) {
  const [zoom, setZoom] = useState(0.25);
  const [offset, setOffset] = useState({ x: 0, y: 0 });

  const grid = useMemo(() => {
    if (!result) return null;
    const lines = [] as JSX.Element[];
    for (let x = 0; x <= width; x += 100) lines.push(<line key={`vx${x}`} x1={x} y1={0} x2={x} y2={height} className={x % 500 === 0 ? 'major' : 'minor'} />);
    for (let y = 0; y <= height; y += 100) lines.push(<line key={`hy${y}`} x1={0} y1={y} x2={width} y2={y} className={y % 500 === 0 ? 'major' : 'minor'} />);
    return lines;
  }, [result, width, height]);

  if (!result) return <section className="card"><h2>Visualização</h2><p>Sem plano para mostrar.</p></section>;

  const formato = String(result.parametros_entrada?.formato || 'circulo');
  const diam = Number(result.parametros_entrada?.['diametro_peca_(mm)'] || 0);
  const w = Number(result.parametros_entrada?.['largura_peca_(mm)'] || 0);
  const h = Number(result.parametros_entrada?.['altura_peca_(mm)'] || 0);
  const pts = (result.parametros_entrada?.poligono_pontos as Array<{ x: number; y: number }> | null) || [];

  return (
    <section className="card">
      <div className="toolbar">
        <h2>Visualização em escala (mm)</h2>
        <div>
          <button className="btn small" onClick={() => setZoom((z) => Math.max(0.1, z - 0.05))}>-</button>
          <span className="zoom">{(zoom * 100).toFixed(0)}%</span>
          <button className="btn small" onClick={() => setZoom((z) => Math.min(1.2, z + 0.05))}>+</button>
        </div>
      </div>
      <div className="svg-wrap" onWheel={(e) => setOffset((o) => ({ ...o, x: o.x - e.deltaX, y: o.y - e.deltaY }))}>
        <svg width={width * zoom} height={height * zoom} viewBox={`${offset.x} ${offset.y} ${width} ${height}`}>
          <g className="grid">{grid}</g>
          <rect x={0} y={0} width={width} height={height} fill="none" stroke="#1f2937" strokeWidth={5} />
          {result.pecas.map((p) => {
            if (formato === 'retangulo') {
              return (
                <g key={p.id}>
                  <rect x={p.x - w / 2} y={p.y - h / 2} width={w} height={h} className="piece" />
                  <text x={p.x} y={p.y} className="piece-text">{p.id}</text>
                </g>
              );
            }
            if (formato === 'poligono' && pts.length > 2) {
              const xs = pts.map((pt) => pt.x);
              const ys = pts.map((pt) => pt.y);
              const cx = (Math.max(...xs) + Math.min(...xs)) / 2;
              const cy = (Math.max(...ys) + Math.min(...ys)) / 2;
              const poly = pts.map((pt) => `${pt.x - cx + p.x},${pt.y - cy + p.y}`).join(' ');
              return (
                <g key={p.id}>
                  <polygon points={poly} className="piece" />
                  <text x={p.x} y={p.y} className="piece-text">{p.id}</text>
                </g>
              );
            }
            return (
              <g key={p.id}>
                <circle cx={p.x} cy={p.y} r={diam / 2} className="piece" />
                <text x={p.x} y={p.y} className="piece-text">{p.id}</text>
              </g>
            );
          })}
        </svg>
      </div>
      <p className="legend">Peças: {result.total_pecas} | Aproveitamento: {result.aproveitamento.toFixed(2)}%</p>
    </section>
  );
}
