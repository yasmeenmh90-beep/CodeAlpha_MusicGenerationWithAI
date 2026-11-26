# Generated artifacts

This repository contains the Python source code for SonataAI.

The pretrained binary checkpoint (`model.pt`), MIDI sample dataset, and example `composition.mid`/`composition.wav` are included in the original project ZIP but are not part of this source-only GitHub upload.

Recreate the demo MIDI files:

```bash
python demo_data.py
```

Train a checkpoint:

```bash
python music.py train --data data --epochs 8
```

Generate a MIDI file and WAV example:

```bash
python music.py generate
```

The checkpoint requires PyTorch. For meaningful genre music, replace the procedural dataset with a properly licensed collection of MIDI performances and train for more epochs. For local use with an already trained checkpoint, you can copy `model.pt` from the supplied SonataAI.zip into the repository directory.
