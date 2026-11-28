# SonataAI Studio

SonataAI Studio is the React 19, TypeScript and Vite frontend for the FastAPI music generation service. The workstation uses a compact sidebar, independently scrolling workspace, six accent presets and a Graphite default. The global Motion toggle controls decorative CSS animation and transitions across workspaces. Theme and motion preferences persist in browser storage. Live audio meters and transport feedback remain active, and CSS also honors the system reduced-motion preference.

## Run locally

From the repository root, start the API.

```bash
python3 -m venv .venv
source .venv/bin/activate
python -m pip install -r requirements-api.txt
python -m uvicorn api:app --port 8000
```

From a second terminal, start the frontend.

```bash
cd studio
npm ci
npm run dev -- --host 127.0.0.1 --port 5173
```

Open http://127.0.0.1:5173. Set `VITE_API_URL` before starting Vite or building for a different API origin. For a different frontend origin, update the API CORS allowlist.

## Workspaces and architecture

- **Studio, AI Composer and Arrangement** cover session overview, LSTM-based composition with MIDI/WAV export and a four-lane timeline for library clips.
- **Piano Studio, Beat Maker, Mixer and Instruments** use Web Audio for polyphonic performance, MIDI recording and editing, step sequencing, drum mixing and oscillator synthesis.
- **Music Library, Visualizer, Training and Analytics** cover saved composition metadata, audio visualization and effects, recorded checkpoint history and library statistics.

`src/main.tsx` owns workspace navigation and appearance preferences. `src/workstation.css` defines the shared shell and controls. `src/workspaces.css` defines the workspace layouts. FastAPI reads the trained PyTorch model and saves generated MIDI/WAV files. The browser stores library metadata, arrangements and appearance preferences locally.

The [application showcase](../README.md#application-showcase) includes all eleven workspaces.

## Build and verify

```bash
npm ci
npm run build
npx playwright install chromium
npm run test:browser
```

Start the API and serve either Vite dev or the production build before running the browser script. For a production preview with the default API CORS configuration, stop the dev server and run `npx vite preview --host 127.0.0.1 --port 5173 --strictPort`. Use `STUDIO_URL` and `VITE_API_URL` to point the script at alternate origins. `CHROME_PATH` optionally selects an installed Chrome executable.

The test runs in a fresh browser context and creates one composition on the configured API. Use a disposable API output directory when preserving an existing collection. The production build passed, all six API tests passed, and headless Chrome passed the regression suite across all eleven workspaces at five viewport widths from 320 to 1440 px. See the [root verification section](../README.md#testing) for the coverage and API warning.

## Limitations

Piano Studio uses a 36-key window where the MIDI range permits. Octave 7 exposes 32 keys through G9 (MIDI 127). The sequencer, drum mixer, instrument synths and Visualizer have separate audio paths. Arrangements reference library audio files and support local session save and playback. Model training runs offline. See the [project limitations](../README.md#known-limitations-and-roadmap) for details.
