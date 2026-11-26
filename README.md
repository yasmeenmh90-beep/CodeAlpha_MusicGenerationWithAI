# SonataAI
A CPU-friendly stacked LSTM music generation prototype. Python 3.11 or 3.12 recommended.

## Run
```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
streamlit run app.py
```
The included model was trained for eight epochs on 12 original, procedurally generated MIDI melodies (11 train, 1 validation). No external music corpus is included. For a meaningful genre model, obtain licensed MIDI files (e.g. public-domain compositions with appropriately licensed MIDI performances), put them in a folder, and train separately using `python music.py train --data /path/to/midi --epochs 30`. Generate with `python music.py generate`. Training replaces the local checkpoint and history.

Preprocessing samples the highest active pitch or rest at 8 Hz. The LSTM predicts the next token using cross entropy, with a file-level validation split. Generation uses temperature sampling and exports MIDI and synthesized WAV. WAV uses a simple harmonic oscillator independent of the MIDI program selection. This version is monophonic, not a chord generator. Streamlit GUI has not been runtime-tested in the build environment. Use locally, not as an unattended multiuser service.
