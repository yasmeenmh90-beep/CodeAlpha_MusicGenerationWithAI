import argparse, json, pathlib, random, wave
import numpy as np
import pretty_midi as pm
import torch
from torch import nn
ROOT=pathlib.Path(__file__).resolve().parent
class Model(nn.Module):
 def __init__(self):
  super().__init__(); self.emb=nn.Embedding(129,32); self.rnn=nn.LSTM(32,64,2,batch_first=True); self.out=nn.Linear(64,129)
 def forward(self,x): return self.out(self.rnn(self.emb(x))[0])
def encode(path):
 m=pm.PrettyMIDI(str(path)); notes=[n for i in m.instruments if not i.is_drum for n in i.notes]; result=[]
 for k in range(int(m.get_end_time()*8)+1):
  active=[n for n in notes if n.start<=k/8<n.end]; result.append(max(active,key=lambda n:n.pitch).pitch if active else 128)
 return result
def train(folder,epochs=15):
 torch.manual_seed(42); torch.set_num_threads(2)
 seqs=[encode(p) for p in pathlib.Path(folder).rglob('*') if p.suffix.lower() in ('.mid','.midi')]; seqs=[s for s in seqs if len(s)>32]
 if not seqs: raise ValueError('Add MIDI files longer than four seconds.')
 random.Random(42).shuffle(seqs); val=seqs[-1:] if len(seqs)>1 else []; tr=seqs[:-1] if val else seqs
 def windows(ss): return torch.tensor([s[j:j+33] for s in ss for j in range(0,len(s)-32,4)],dtype=torch.long)
 x=windows(tr); model=Model(); opt=torch.optim.Adam(model.parameters(),lr=.003); history=[]
 for ep in range(epochs):
  model.train(); total=0
  for b in x[torch.randperm(len(x))].split(64):
   opt.zero_grad(); loss=nn.functional.cross_entropy(model(b[:,:-1]).reshape(-1,129),b[:,1:].reshape(-1)); loss.backward(); opt.step(); total+=loss.item()*len(b)
  row={'epoch':ep+1,'loss':total/len(x)}
  if val:
   model.eval(); v=windows(val)
   with torch.no_grad():
    losses=[]; correct=0; count=0
    for b in v.split(64):
     logits=model(b[:,:-1]); target=b[:,1:]; losses.append((nn.functional.cross_entropy(logits.reshape(-1,129),target.reshape(-1)).item(),target.numel())); correct+=(logits.argmax(-1)==target).sum().item(); count+=target.numel()
    row.update(val_loss=sum(a*n for a,n in losses)/count,val_accuracy=correct/count)
  history.append(row); print(row)
 torch.save({'weights':model.state_dict(),'seed':tr[0][:32]},ROOT/'model.pt'); (ROOT/'history.json').write_text(json.dumps(history)); return history

def generate(length=128,temperature=.9,bpm=100,program=0,seed=42):
 if not 0<temperature<=3 or not 30<=bpm<=240 or not 1<=length<=4096 or not 0<=program<=127: raise ValueError('Invalid generation settings')
 torch.set_num_threads(2); torch.manual_seed(seed); ck=torch.load(ROOT/'model.pt',map_location='cpu',weights_only=True); model=Model(); model.load_state_dict(ck['weights']); model.eval(); context=ck['seed'].copy(); out=[]
 with torch.no_grad():
  for _ in range(length):
   logits=model(torch.tensor([context[-32:]]))[0,-1]; n=torch.multinomial(torch.softmax(logits/temperature,dim=0),1).item(); context.append(n); out.append(n)
 m=pm.PrettyMIDI(initial_tempo=bpm); inst=pm.Instrument(program); step=60/bpm/4; start=0
 for k in range(1,len(out)+1):
  if k==len(out) or out[k]!=out[start]:
   if out[start]<128: inst.notes.append(pm.Note(velocity=85,pitch=out[start],start=start*step,end=k*step))
   start=k
 m.instruments.append(inst); return m,out

def export(m,path):
 path=pathlib.Path(path); m.write(str(path.with_suffix('.mid'))); sr=22050; audio=np.zeros(max(1,int((m.get_end_time()+.2)*sr)),dtype=np.float32)
 for inst in m.instruments:
  for n in inst.notes:
   a,b=int(n.start*sr),int(n.end*sr); t=np.arange(b-a)/sr; f=440*2**((n.pitch-69)/12); env=np.minimum(1,t/.015)*np.minimum(1,(len(t)-np.arange(len(t)))/(sr*.04)); audio[a:b]+=.25*env*(np.sin(2*np.pi*f*t)+.25*np.sin(4*np.pi*f*t))
 with wave.open(str(path.with_suffix('.wav')),'wb') as w: w.setparams((1,2,sr,0,'NONE','not compressed')); w.writeframes((np.clip(audio,-1,1)*32767).astype('<i2').tobytes())
if __name__=='__main__':
 p=argparse.ArgumentParser(); p.add_argument('action',choices=['train','generate']); p.add_argument('--data',default='data'); p.add_argument('--epochs',type=int,default=15); a=p.parse_args(); train(a.data,a.epochs) if a.action=='train' else export(generate()[0],ROOT/'composition')
