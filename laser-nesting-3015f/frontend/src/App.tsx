import { useState } from 'react';
import InputForm from './components/InputForm';
import ResultsPanel from './components/ResultsPanel';
import VisualizationSVG from './components/VisualizationSVG';
import { PlanParams, PlanResult, createPlan } from './services/api';

const defaultParams: PlanParams = {
  largura_chapa: 3000,
  altura_chapa: 1500,
  espessura: 3,
  margem_borda: 10,
  formato: 'circulo',
  diametro_peca: 127,
  largura_peca: 120,
  altura_peca: 80,
  poligono_pontos: [{ x: 0, y: 0 }, { x: 120, y: 0 }, { x: 80, y: 100 }],
  kerf_laser: 1.5,
  spacing: 2,
  velocidade_corte: 35,
  lead_in_mm: 0,
  lead_out_mm: 0,
  metodo_preferido: 'auto'
};

export default function App() {
  const [params, setParams] = useState<PlanParams>(defaultParams);
  const [result, setResult] = useState<PlanResult | null>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');

  const run = async () => {
    try {
      setLoading(true);
      setError('');
      setResult(await createPlan(params));
    } catch (e) {
      setError((e as Error).message);
    } finally {
      setLoading(false);
    }
  };

  return (
    <main className="app">
      <header className="topbar">
        <h1>Laser Nesting 3015F</h1>
        <p>Planejamento de corte em mm (Circulo, Retangulo, Poligono)</p>
      </header>
      {error && <div className="error" role="alert">{error}</div>}
      <section className="layout" aria-label="Layout principal">
        <InputForm values={params} onChange={setParams} onSubmit={run} loading={loading} />
        <div className="right-col">
          <ResultsPanel result={result} params={params} />
          <VisualizationSVG result={result} width={params.largura_chapa} height={params.altura_chapa} />
        </div>
      </section>
    </main>
  );
}
