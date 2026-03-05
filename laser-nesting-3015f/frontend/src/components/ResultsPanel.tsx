import { PlanParams, PlanResult, dxfUrl } from '../services/api';

type Props = {
  result: PlanResult | null;
  params: PlanParams;
};

const formatTime = (seconds: number) => {
  const min = Math.floor(seconds / 60);
  const sec = Math.round(seconds % 60);
  return `${min}m ${sec}s`;
};

export default function ResultsPanel({ result, params }: Props) {
  const exportJson = () => {
    if (!result) return;
    const blob = new Blob([JSON.stringify(result, null, 2)], { type: 'application/json' });
    const url = URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = 'plano_nesting.json';
    a.click();
    URL.revokeObjectURL(url);
  };

  if (!result) return <section className="card"><h2>Resultados</h2><p>Preencha e gere o plano.</p></section>;

  return (
    <section className="card" aria-live="polite">
      <h2>Resultados</h2>
      <ul className="metrics">
        <li>Total de peças: <strong>{result.total_pecas}</strong></li>
        <li>Método: <strong>{result.metodo_escolhido}</strong></li>
        <li>Linhas/colunas: <strong>{result.linhas}/{result.colunas_estimadas}</strong></li>
        <li>Aproveitamento: <strong>{result.aproveitamento.toFixed(2)}%</strong></li>
        <li>Comprimento de corte: <strong>{result.comprimento_corte_total.toFixed(2)} mm</strong></li>
        <li>Tempo estimado: <strong>{formatTime(result.tempo_estimado)}</strong></li>
      </ul>
      <div className="actions">
        <a className="btn" href={dxfUrl(params)}>Exportar DXF</a>
        <button className="btn" onClick={exportJson}>Exportar JSON</button>
        {result.svg_inline && (
          <a
            className="btn"
            href={`data:image/svg+xml;charset=utf-8,${encodeURIComponent(result.svg_inline)}`}
            target="_blank"
            rel="noreferrer"
          >
            Abrir SVG
          </a>
        )}
      </div>
    </section>
  );
}
