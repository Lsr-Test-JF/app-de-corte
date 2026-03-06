import { FormEvent, useMemo, useState } from 'react';
import { PlanParams } from '../services/api';

type Props = {
  values: PlanParams;
  onChange: (next: PlanParams) => void;
  onSubmit: () => void;
  loading: boolean;
};

const commonFields: Array<{ key: keyof PlanParams; label: string; min?: number; step?: number }> = [
  { key: 'largura_chapa', label: 'Largura da chapa (mm)', min: 1, step: 1 },
  { key: 'altura_chapa', label: 'Altura da chapa (mm)', min: 1, step: 1 },
  { key: 'margem_borda', label: 'Margem de borda (mm)', min: 0, step: 0.1 },
  { key: 'espessura', label: 'Espessura (mm)', min: 0.1, step: 0.1 },
  { key: 'kerf_laser', label: 'Kerf laser (mm)', min: 0, step: 0.1 },
  { key: 'spacing', label: 'Espaçamento entre peças (mm)', min: 0, step: 0.1 },
  { key: 'velocidade_corte', label: 'Velocidade corte (mm/s)', min: 0.1, step: 0.1 },
  { key: 'lead_in_mm', label: 'Lead-in (mm)', min: 0, step: 0.1 },
  { key: 'lead_out_mm', label: 'Lead-out (mm)', min: 0, step: 0.1 }
];

export default function InputForm({ values, onChange, onSubmit, loading }: Props) {
  const [polygonText, setPolygonText] = useState('0,0\n120,0\n80,100');

  const shapeFields = useMemo(() => {
    if (values.formato === 'circulo') return [{ key: 'diametro_peca', label: 'Diâmetro peça (mm)' }];
    if (values.formato === 'retangulo') return [{ key: 'largura_peca', label: 'Largura peça (mm)' }, { key: 'altura_peca', label: 'Altura peça (mm)' }];
    return [];
  }, [values.formato]);

  const handleSubmit = (e: FormEvent) => {
    e.preventDefault();
    if (values.formato === 'poligono') {
      const pts = polygonText
        .split('\n')
        .map((line) => line.trim())
        .filter(Boolean)
        .map((line) => {
          const [x, y] = line.split(',').map((v) => Number(v.trim()));
          return { x, y };
        })
        .filter((p) => Number.isFinite(p.x) && Number.isFinite(p.y));
      onChange({ ...values, poligono_pontos: pts });
    }
    onSubmit();
  };

  return (
    <form className="card form" onSubmit={handleSubmit} aria-label="Formulário de parâmetros">
      <h2>Parâmetros</h2>

      <label className="field">
        <span>Formato</span>
        <select
          value={values.formato}
          onChange={(e) => onChange({ ...values, formato: e.target.value as PlanParams['formato'] })}
        >
          <option value="circulo">Circulo</option>
          <option value="retangulo">Retangulo</option>
          <option value="poligono">Poligono Pontos (x,y por linha)</option>
        </select>
      </label>

      {commonFields.map((field) => (
        <label className="field" key={field.key}>
          <span>{field.label}</span>
          <input
            type="number"
            min={field.min}
            step={field.step}
            value={(values[field.key] as number) ?? ''}
            onChange={(e) => onChange({ ...values, [field.key]: Number(e.target.value) })}
          />
        </label>
      ))}

      {shapeFields.map((field) => (
        <label className="field" key={field.key}>
          <span>{field.label}</span>
          <input
            type="number"
            min={0.1}
            step={0.1}
            value={(values[field.key as keyof PlanParams] as number) ?? ''}
            onChange={(e) => onChange({ ...values, [field.key]: Number(e.target.value) })}
          />
        </label>
      ))}

      {values.formato === 'poligono' && (
        <label className="field">
          <span>Pontos (x,y por linha)</span>
          <textarea
            rows={6}
            value={polygonText}
            onChange={(e) => setPolygonText(e.target.value)}
            placeholder="0,0&#10;120,0&#10;80,100"
          />
        </label>
      )}

      <label className="field">
        <span>Método preferido</span>
        <select
          value={values.metodo_preferido}
          onChange={(e) => onChange({ ...values, metodo_preferido: e.target.value as PlanParams['metodo_preferido'] })}
        >
          <option value="auto">Auto</option>
          <option value="grid">Grid</option>
          <option value="hex">Hexagonal</option>
        </select>
      </label>
      <button className="btn" disabled={loading}>{loading ? 'Calculando...' : 'Gerar plano'}</button>
    </form>
  );
}
