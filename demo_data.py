from pathlib import Path
import pretty_midi as pm
import random
p=Path(__file__).parent/'data'; p.mkdir(exist_ok=True)
for k in range(12):
 r=random.Random(k); m=pm.PrettyMIDI(); i=pm.Instrument(0); scale=[60,62,64,65,67,69,71,72]; t=0
 for j in range(64):
  n=scale[(j//4+j%4+r.choice([0,0,1]))%8]+(k%3)*2; d=r.choice([.25,.25,.5]); i.notes.append(pm.Note(80,n,t,t+d)); t+=d
 m.instruments.append(i); m.write(str(p/f'original_demo_{k}.mid'))
