# SonataAI V4 development

From the repository root, install Python dependencies with `python -m pip install -r requirements-api.txt`, then run `python -m uvicorn api:app --port 8000`. In another terminal run `cd studio && npm install && npm run dev -- --port 5173`. Use http://localhost:5173. This is a local development setup; no authentication or production hosting is configured. Generated tracks accumulate in studio_outputs; remove them when no longer needed.
