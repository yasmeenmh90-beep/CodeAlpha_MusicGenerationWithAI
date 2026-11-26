# SonataAI V4 Studio

React / TypeScript / Web Audio frontend with FastAPI and PyTorch LSTM backend.

## Local development (no Docker)

From the repository root:
```sh
python3 -m venv .venv
source .venv/bin/activate
python -m pip install -r requirements-api.txt
python -m uvicorn api:app --port 8000
```
In a second terminal:
```sh
cd studio
npm install
npm run dev -- --port 5173
```
Open http://localhost:5173.

## Verification
Backend: install pytest and httpx, then run python -m pytest tests/test_studio_api.py -q from root.
Frontend: cd studio && npm run build.
CI runs both checks on pushes and pull requests. Browser audio tests remain manual.

## Deployment
Build the frontend with npm run build; output is studio/dist.
Set VITE_API_URL before building. Serve the frontend and API behind HTTPS, configure API CORS for the deployed origin, and provide persistent writable storage for studio_outputs. The current API is intended for trusted local use: public hosting requires authentication, quotas, output cleanup and resource limits. No public deployment is provisioned.

## Limitations
Original model is monophonic; genre conditioning requires separately licensed labelled data and training. MIDI program selection does not change the original WAV synth. Library metadata is browser-local. Drum mixer does not mix generated tracks. Training page is a placeholder. V3 Streamlit entry point remains available.
