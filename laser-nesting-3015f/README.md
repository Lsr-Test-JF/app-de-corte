# laser-nesting-3015f

Planejador de nesting circular para laser 3015F 3kW (unidade em **mm**), com backend FastAPI, frontend React+TS e versão simplificada em Streamlit.

## Estrutura
- `backend/`: API e núcleo geométrico
- `frontend/`: UI web industrial simplificada
- `streamlit_app/`: app único para protótipo rápido
- `examples/`: payload e output de exemplo

## Requisitos
- Python 3.10+
- Node 20+

## Backend (FastAPI)
```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
PYTHONPATH=backend uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

Endpoints:
- `POST /api/v1/plan`
- `GET /api/v1/plan/dxf`
- `POST /api/v1/visual`

## Frontend (React + TypeScript)
```bash
cd frontend
npm install
npm run dev
```
Acesse: `http://localhost:5173`

## Streamlit (modo simples)
```bash
SIMPLE_UI=true PYTHONPATH=backend:. streamlit run streamlit_app/app_streamlit.py
```

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

## Exportações
- DXF: `GET /api/v1/plan/dxf` (download direto)
- JSON: retorno de `POST /api/v1/plan`

