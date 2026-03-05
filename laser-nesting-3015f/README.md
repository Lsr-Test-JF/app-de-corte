# laser-nesting-3015f

Planejador de nesting circular para laser 3015F 3kW (unidade em **mm**), com backend FastAPI, frontend React+TS e versão simplificada em Streamlit.

## Estrutura
- `backend/`: API e núcleo geométrico
- `frontend/`: UI web (também funciona no GitHub Pages sem backend)
- `streamlit_app/`: app único para protótipo rápido
- `examples/`: payload e output de exemplo

## Rodar agora (local)
### Backend (FastAPI)
```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
PYTHONPATH=backend uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

### Frontend (React + TypeScript)
```bash
cd frontend
npm install
VITE_API_URL=http://localhost:8000 npm run dev
```
Acesse: `http://localhost:5173`

### Streamlit (modo simples)
```bash
SIMPLE_UI=true PYTHONPATH=backend:. streamlit run streamlit_app/app_streamlit.py
```

## Deploy no GitHub Pages (pronto)
1. Suba este projeto para um repositório no GitHub.
2. Em **Settings → Pages**, selecione **GitHub Actions** como source.
3. (Opcional) Em **Settings → Secrets and variables → Actions → Variables**, crie:
   - `VITE_API_URL=https://seu-backend.onrender.com`
4. Faça push na branch `main` ou `work`.
5. O workflow `.github/workflows/pages.yml` publica automaticamente.

> Se `VITE_API_URL` não for definido, o frontend roda em modo local no navegador (sem backend) para cálculo/visualização/export JSON/DXF local.


## Formatos suportados
- `circulo`: usar `diametro_peca_(mm)`
- `retangulo`: usar `largura_peca_(mm)` + `altura_peca_(mm)`
- `poligono`: usar `poligono_pontos` com pontos `(x,y)` por linha no frontend

Exemplo de `parametros_entrada` no retorno:
```json
{
  "largura_chapa_(mm)": 3000.0,
  "altura_chapa_(mm)": 1500.0,
  "espessura_(mm)": 3.0,
  "margem_borda_(mm)": 10.0,
  "formato": "circulo",
  "diametro_peca_(mm)": 127.0,
  "kerf_laser_(mm)": 1.5,
  "Espaçamento_entre_peças_(mm)": 2.0,
  "lead_in_mm": 0.0,
  "lead_out_mm": 0.0,
  "metodo_preferido": "auto"
}
```

## Endpoints backend
- `POST /api/v1/plan`
- `POST /api/v1/plan/dxf`
- `POST /api/v1/visual`

## Testes
```bash
PYTHONPATH=backend pytest backend/tests -q
```

## Docker
```bash
docker compose up --build
```
- Backend: `http://localhost:8000`
- Frontend: `http://localhost:5173`

## Exemplo de payload
Arquivo: `examples/ex1_params.json`.

## Exemplo de saída
Arquivo: `examples/ex1_output.json`.
