import pathlib
import pretty_midi as pm
p=pathlib.Path(__file__).resolve().parent/'data';p.mkdir(exist_ok=True)
for k in range(12):
 m=pm.PrettyMIDI();i=pm.Instrument(0)
 notes=[60,62,64,67,69,67,64,62,60,64,67,72]
 for j in range(48):
  pitch=notes[(j+k)%len(notes)]+(k%3-1)*2
  i.notes.append(pm.Note(90,pitch,j*.25,(j+1)*.25-.025))
 m.instruments.append(i);m.write(str(p/f'original_demo_{k}.mid'))
print('Created 12 original MIDI melodies.')
