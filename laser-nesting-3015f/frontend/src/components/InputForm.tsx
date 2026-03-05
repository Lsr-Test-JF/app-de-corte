import { FormEvent } from 'react';
import { PlanParams } from '../services/api';

type Props = {
  values: PlanParams;
  onChange: (next: PlanParams) => void;
  onSubmit: () => void;
  loading: boolean;
};

const fields: Array<{ key: keyof PlanParams; label: string; min?: number; step?: number }> = [
  { key: 'largura_chapa', label: 'Largura da chapa (mm)', min: 1, step: 1 },
  { key: 'altura_chapa', label: 'Altura da chapa (mm)', min: 1, step: 1 },
  { key: 'margem_borda', label: 'Margem de borda (mm)', min: 0, step: 0.1 },
  { key: 'espessura', label: 'Espessura (mm)', min: 0.1, step: 0.1 },
  { key: 'diametro_peca', label: 'Diâmetro peça (mm)', min: 1, step: 0.1 },
  { key: 'kerf_laser', label: 'Kerf (mm)', min: 0, step: 0.1 },
  { key: 'spacing', label: 'Spacing (mm)', min: 0, step: 0.1 },
  { key: 'velocidade_corte', label: 'Velocidade corte (mm/s)', min: 0.1, step: 0.1 },
  { key: 'lead_in_mm', label: 'Lead-in (mm)', min: 0, step: 0.1 },
  { key: 'lead_out_mm', label: 'Lead-out (mm)', min: 0, step: 0.1 }
];

export default function InputForm({ values, onChange, onSubmit, loading }: Props) {
  const handleSubmit = (e: FormEvent) => {
    e.preventDefault();
    onSubmit();
  };

  return (
    <form className="card form" onSubmit={handleSubmit} aria-label="Formulário de parâmetros">
      <h2>Parâmetros</h2>
      {fields.map((field) => (
        <label className="field" key={field.key}>
          <span>{field.label}</span>
          <input
            type="number"
            min={field.min}
            step={field.step}
            value={values[field.key] as number}
            onChange={(e) => onChange({ ...values, [field.key]: Number(e.target.value) })}
          />
        </label>
      ))}
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
