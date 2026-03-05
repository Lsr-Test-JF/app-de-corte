#!/usr/bin/env bash
set -e
if [ "${SIMPLE_UI:-false}" = "true" ]; then
  PYTHONPATH=backend:. streamlit run streamlit_app/app_streamlit.py
else
  cd frontend
  npm install
  npm run dev -- --host 0.0.0.0 --port 5173
fi
