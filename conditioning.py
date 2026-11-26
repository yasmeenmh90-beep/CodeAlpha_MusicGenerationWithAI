"""Optional genre-conditioned LSTM; train only on appropriately licensed labelled MIDI."""
import argparse
import json
from pathlib import Path
import random
import torch
from torch import nn
import pretty_midi as pm
import music

GENRES = ("ambient", "classical", "electronic", "jazz", "cinematic", "lofi")
SCALES = {"chromatic": tuple(range(12)), "major": (0,2,4,5,7,9,11), "minor": (0,2,3,5,7,8,10), "pentatonic": (0,2,4,7,9)}
CHECKPOINT = music.ROOT / "conditioned.pt"

class Conditioned(nn.Module):
    def __init__(self):
        super().__init__()
        self.notes = nn.Embedding(129, 32)
        self.genres = nn.Embedding(len(GENRES), 16)
        self.rnn = nn.LSTM(48, 64, 2, batch_first=True)
        self.out = nn.Linear(64,129)

    def forward(self, x, genre):
        g = self.genres(genre).unsqueeze(1).expand(-1,x.shape[1],-1)
        return self.out(self.rnn(torch.cat((self.notes(x),g),dim=-1))[0])

def constrain(midi, tokens, root, scale):
    allowed = {(root+x)%12 for x in SCALES[scale]}
    def snap(p):
        if p == 128:
            return p
        return min((k for k in range(128) if k%12 in allowed),key=lambda k: (abs(k-p),k))
    for inst in midi.instruments:
        if not inst.is_drum:
            for note in inst.notes:
                note.pitch = snap(note.pitch)
    return midi, [snap(p) for p in tokens]

def train(folder, epochs=15):
    torch.manual_seed(42)
    rng = random.Random(42)
    train_rows, val_rows, seeds = [], [], {}
    for i, genre in enumerate(GENRES):
        paths = sorted(p for p in (Path(folder)/genre).rglob("*") if p.suffix.lower() in (".mid",".midi"))
        seqs = [music.encode(p) for p in paths]
        seqs = [s for s in seqs if len(s)>32]
        if len(seqs)<2:
            raise ValueError(f"{genre}: provide at least two distinct MIDI pieces longer than four seconds")
        rng.shuffle(seqs)
        seeds[genre] = seqs[0][:32]
        nval = max(1,len(seqs)//5)
        for group, target in ((seqs[:-nval],train_rows),(seqs[-nval:],val_rows)):
            for seq in group:
                target.extend((seq[j:j+33],i) for j in range(0,len(seq)-32,4))
    def tensors(rows):
        return torch.tensor([x for x,_ in rows],dtype=torch.long),torch.tensor([g for _,g in rows],dtype=torch.long)
    x,g = tensors(train_rows)
    v,h = tensors(val_rows)
    model = Conditioned()
    opt = torch.optim.Adam(model.parameters(),lr=.003)
    history=[]
    def evaluate():
        model.eval()
        loss=correct=count=0
        with torch.no_grad():
            for b,c in zip(v.split(64),h.split(64)):
                logits=model(b[:,:-1],c).reshape(-1,129)
                y=b[:,1:].reshape(-1)
                loss+=nn.functional.cross_entropy(logits,y,reduction="sum").item()
                correct+=(logits.argmax(-1)==y).sum().item()
                count+=y.numel()
        return loss/count,correct/count
    for epoch in range(epochs):
        model.train()
        total=count=0
        for idx in torch.randperm(len(x)).split(64):
            b,c=x[idx],g[idx]
            opt.zero_grad()
            loss=nn.functional.cross_entropy(model(b[:,:-1],c).reshape(-1,129),b[:,1:].reshape(-1))
            loss.backward()
            opt.step()
            total+=loss.item()*b.numel()
            count+=b.numel()
        vl,va=evaluate()
        row={"epoch":epoch+1,"loss":total/count,"val_loss":vl,"val_accuracy":va}
        history.append(row)
        print(row)
    torch.save({"weights":model.state_dict(),"seeds":seeds},CHECKPOINT)
    (music.ROOT/"conditioned_history.json").write_text(json.dumps(history))
    return history

def generate(genre, length, temperature, bpm, program, seed):
    torch.manual_seed(seed)
    ck=torch.load(CHECKPOINT,map_location="cpu",weights_only=True)
    model=Conditioned()
    model.load_state_dict(ck["weights"])
    model.eval()
    context=list(ck["seeds"][genre])
    g=torch.tensor([GENRES.index(genre)])
    out=[]
    with torch.no_grad():
        for _ in range(length):
            logits=model(torch.tensor([context[-32:]]),g)[0,-1]
            n=torch.multinomial(torch.softmax(logits/temperature,dim=0),1).item()
            context.append(n)
            out.append(n)
    midi=pm.PrettyMIDI(initial_tempo=bpm)
    inst=pm.Instrument(program)
    step=60/bpm/4
    start=0
    for k in range(1,len(out)+1):
        if k==len(out) or out[k]!=out[start]:
            if out[start]<128:
                inst.notes.append(pm.Note(velocity=85,pitch=out[start],start=start*step,end=k*step))
            start=k
    midi.instruments.append(inst)
    return midi,out

if __name__=="__main__":
    parser=argparse.ArgumentParser()
    parser.add_argument("--data",default="genre_data")
    parser.add_argument("--epochs",type=int,default=15)
    args=parser.parse_args()
    if args.epochs<1: parser.error("epochs must be positive")
    train(args.data,args.epochs)
