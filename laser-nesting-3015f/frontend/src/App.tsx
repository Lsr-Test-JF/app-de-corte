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
  diametro_peca: 127,
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
        <p>Planejamento de corte circular em mm</p>
      </header>
      {error && <div className="error">{error}</div>}
      <section className="layout">
        <InputForm values={params} onChange={setParams} onSubmit={run} loading={loading} />
        <div className="right-col">
          <ResultsPanel result={result} params={params} />
          <VisualizationSVG result={result} width={params.largura_chapa} height={params.altura_chapa} />
        </div>
      </section>
    </main>
  );
}
