# SonataAI Studio

React 19 / TypeScript / Vite frontend for the FastAPI music generation service.

See the [main project README](../README.md) for all eleven workspaces, model architecture, training results, API reference, installation, testing and limitations.

## Start locally

From the repository root:

```bash
python3 -m venv .venv
source .venv/bin/activate
python -m pip install -r requirements-api.txt
python -m uvicorn api:app --port 8000
```

In another terminal from the root:

```bash
cd studio
npm install
npm run dev -- --port 5173
```

Open http://localhost:5173. Use VITE_API_URL for a custom API origin.

## Build and verify

```bash
npm run build
```

This performs TypeScript checks and produces dist/. The repository CI also defines backend pytest checks. Latest execution and browser audio verification are not confirmed.

## UI implementation

StudioHome: overview; Player: AI Composer; Arrangement: clip sessions; Piano: performance and MIDI; Beat: drum sequencer and mixer; Instruments: oscillator voices; Library: local catalog; GlobalDeck: audio visualization and playback effects; Training: recorded history; Analytics: saved composition statistics.

The original Streamlit interface is preserved. Training runs offline. Browser storage and audio engines are local; audio routing is not unified. See the main README for detailed limitations and deployment requirements.
