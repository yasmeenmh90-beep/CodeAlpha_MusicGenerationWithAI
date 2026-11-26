import streamlit as st
import tempfile, pathlib, json, io, wave, base64, html
import numpy as np
import pandas as pd
import altair as alt
import pretty_midi as pm
from music import ROOT, generate, export, train
st.set_page_config(page_title='SonataAI | Production Studio',page_icon='🎹',layout='wide')
st.markdown("""<style>
.stApp{background:#0a0b12;color:#f0efff}.block-container{max-width:1550px;padding:1.5rem 2rem 3rem}[data-testid=stHeader]{background:transparent}[data-testid=stSidebar]{background:#11121d;border-right:1px solid #292b40;min-width:210px}[data-testid=stSidebar] [data-testid=stMarkdownContainer] p{font-size:13px}.hero{padding:24px 30px;border:1px solid #41355f;border-radius:18px;background:radial-gradient(circle at 84% 40%,#953b9c55,transparent 33%),linear-gradient(115deg,#211747,#101c32);margin-bottom:12px}.hero h1{font-size:42px;letter-spacing:-2px;margin:4px 0;color:white}.hero p{color:#bdbbd8;margin:4px 0}.eyebrow,.section{font-size:11px;letter-spacing:2px;color:#67e8f9;font-weight:800}.brand{font-size:29px;font-weight:900;color:#d8b4fe}.muted{color:#a4a6bd;font-size:12px}.tile{padding:14px;border-radius:12px;background:#171926;border:1px solid #303247;border-left:3px solid var(--accent)}.tile small{color:#aaaec8;letter-spacing:1px}.tile b{display:block;font-size:23px;color:var(--accent)}[data-testid=stMetric]{background:#171926;padding:10px;border-radius:10px}[data-testid=stMetricValue]{font-size:22px!important}div.stButton>button[kind=primary]{background:linear-gradient(100deg,#7434e9,#e73993);border:0;font-weight:800;min-height:48px}[data-testid=stVerticalBlockBorderWrapper]{border-color:#303247;border-radius:16px}.art{padding:18px;border-radius:16px;background:linear-gradient(120deg,#271951,#1d2543);display:flex;gap:22px;align-items:center}.record{width:112px;height:112px;flex-shrink:0;border-radius:50%;background:repeating-radial-gradient(circle,#191925 0 2px,#333044 3px 4px,#15151e 5px 7px);position:relative;box-shadow:0 0 28px #a855f755}.record:after{content:'';position:absolute;inset:36%;border-radius:50%;background:radial-gradient(circle,#12121d 0 10%,#f472b6 12% 35%,#8b5cf6 36%)}.art strong{font-size:26px}.rack{display:flex;gap:5px;height:45px;align-items:center}.rack i{flex:1;background:linear-gradient(#22d3ee,#a855f7,#ec4899);border-radius:3px}.transport{font:12px monospace;color:#a5f3fc;letter-spacing:2px;padding:10px 0}.keyboard{display:flex;height:68px;position:relative;margin:8px 0}.key{flex:1;background:#e7e8f2;border:1px solid #161826;border-radius:0 0 4px 4px;color:#39394c;display:flex;align-items:end;justify-content:center;font-size:9px;padding-bottom:5px}.key.active{background:#c4b5fd}.key.black{background:#282837;color:#ddd;position:absolute;width:4%;height:63%;z-index:1}.key.black.active{background:#db2777}.presets{display:grid;grid-template-columns:repeat(4,1fr);gap:9px;margin:8px 0}.preset{padding:12px;border-radius:12px;background:#161827;border-top:3px solid var(--c);font-size:12px;color:#d7d8ec}.preset b{display:block;color:var(--c);font-size:14px}@media(max-width:700px){.presets{grid-template-columns:repeat(2,1fr)}.hero h1{font-size:30px}}
</style>""",unsafe_allow_html=True)
import streamlit.components.v1 as components

def player(audio):
    encoded=base64.b64encode(audio).decode('ascii')
    components.html(f'<html><body style="margin:0;background:#11121d"><audio controls preload="metadata" style="width:100%;height:50px" src="data:audio/wav;base64,{encoded}"></audio></body></html>',height=58)

def keyboard(notes):
    active={n['pitch']%12 for n in notes}; white=[0,2,4,5,7,9,11]; names=['C','D','E','F','G','A','B']; keys=[]
    for octave in range(2):
        for pitch,name in zip(white,names): keys.append(f'<div class="key {"active" if pitch in active else ""}">{name}{octave+4}</div>')
    for octave in range(2):
        for slot,pitch in [(1,1),(2,3),(4,6),(5,8),(6,10)]: keys.append(f'<div class="key black {"active" if pitch in active else ""}" style="left:{(octave*7+slot)/14*100-2}%"></div>')
    st.markdown('<div class="keyboard">'+''.join(keys)+'</div>',unsafe_allow_html=True)
def tile(label,value,color):
 st.markdown(f'<div class="tile" style="--accent:{color}"><small>{label}</small><b>{value}</b></div>',unsafe_allow_html=True)
def pack(midi,audio,name,bpm=None):
 m=pm.PrettyMIDI(io.BytesIO(midi)); notes=[{'start':n.start,'end':n.end,'pitch':n.pitch,'velocity':n.velocity} for i in m.instruments for n in i.notes]
 return dict(midi=midi,audio=audio,name=name,bpm=bpm or 100,notes=notes)
# Avoid tempo estimation for short or unusual MIDI files.
def sample():
 return pack((ROOT/'composition.mid').read_bytes(),(ROOT/'composition.wav').read_bytes(),'Original demo',100)
if 'library' not in st.session_state: st.session_state.library=[]
if 'result' not in st.session_state and (ROOT/'composition.mid').exists() and (ROOT/'composition.wav').exists(): st.session_state.result=sample()
with st.sidebar:
 st.markdown('<div class="brand">◈ SonataAI</div><div class="muted">NEURAL SOUND LAB / V3</div>',unsafe_allow_html=True)
 st.divider(); page=st.radio('WORKSPACE',['🎛  Create music','💿  My library','🧠  Training lab','📊  Analytics'],label_visibility='collapsed')
 st.divider()
 st.caption('ENGINE STATUS')
 if (ROOT/'model.pt').exists(): st.success('LSTM checkpoint ready')
 else: st.warning('Training required')
 st.caption('Local inference · Python / PyTorch\n\nCodeAlpha • Task 03')
if page.startswith('🎛'):
 st.markdown('<div class="hero"><div class="eyebrow">✦ GENERATIVE AUDIO WORKSPACE</div><h1>Your next sound starts here.</h1><p>COMPOSE / SEQUENCE / LISTEN / EXPORT · Neural audio workstation</p></div>',unsafe_allow_html=True)
 cols=st.columns(3)
 for col,label,value,color in zip(cols,['MODEL','ENGINE','SESSION TRACKS'],['LSTM','MIDI + WAV',str(len(st.session_state.library))],['#c4b5fd','#67e8f9','#fbbf24']):
  with col: tile(label,value,color)
 st.markdown('<div class="presets"><div class="preset" style="--c:#c084fc"><b>01 / Dreamscape</b> Atmospheric keys</div><div class="preset" style="--c:#fbbf24"><b>02 / Classical</b> Piano sketch</div><div class="preset" style="--c:#22d3ee"><b>03 / Jazz</b> Expressive rhythm</div><div class="preset" style="--c:#f472b6"><b>04 / Experimental</b> Unusual patterns</div></div>',unsafe_allow_html=True)
 left,right=st.columns([1,2],gap='medium')
 with left:
  with st.container(border=True):
   st.subheader('🎛 Synth rack'); st.caption('Choose a settings preset (not a genre-trained model).')
   presets={'Dreamscape':(80,.75,128,4),'Classical sketch':(100,.65,128,0),'Jazz sketch':(120,1.15,192,0),'Experimental':(135,1.65,256,24)}
   preset=st.selectbox('Creative preset',list(presets)); b,t,l,p=presets[preset]
   bpm=st.slider('Tempo · BPM',60,180,b,key=f'bpm-{preset}'); temp=st.slider('Creativity',.1,2.,t,key=f'temp-{preset}'); length=st.slider('Sequence steps',32,512,l,step=16,key=f'len-{preset}')
   instruments={'Grand piano':0,'Electric piano':4,'Guitar':24,'Violin':40,'Synth pad':89}; names=list(instruments); inst=st.selectbox('MIDI instrument',names,index=list(instruments.values()).index(p),key=f'inst-{preset}'); seed=st.number_input('Random seed',0,100000,42)
   if st.button('✦ Generate music',type='primary',use_container_width=True):
    try:
     with st.spinner('Composing with the LSTM…'):
      m,_=generate(length,temp,bpm,instruments[inst],seed)
      with tempfile.TemporaryDirectory() as d:
       path=pathlib.Path(d)/'track'; export(m,path); st.session_state.result=pack(path.with_suffix('.mid').read_bytes(),path.with_suffix('.wav').read_bytes(),preset,bpm)
    except Exception as exc: st.error(str(exc))
 with right:
  r=st.session_state.get('result')
  if r:
   with st.container(border=True):
    st.markdown('<div class="art"><div class="record"></div><div><div class="eyebrow">NOW PLAYING / STUDIO DECK</div><strong>Sound canvas</strong><p>Neural composition · Master output</p><div class="transport">STEREO UI / MONO WAV</div></div></div>',unsafe_allow_html=True)
    st.subheader(r['name']); player(r['audio'])
    with wave.open(io.BytesIO(r['audio'])) as w:
     sr=w.getframerate(); signal=np.frombuffer(w.readframes(w.getnframes()),dtype='<i2').astype(float)/32768
    duration=len(signal)/sr; chunks=np.array_split(signal,min(130,len(signal))); peaks=pd.DataFrame({'Time':np.linspace(0,duration,len(chunks)),'low': [float(c.min()) for c in chunks],'high':[float(c.max()) for c in chunks]})
    st.altair_chart(alt.Chart(peaks).mark_rule(color='#22d3ee',strokeWidth=2).encode(x=alt.X('Time:Q',title='Seconds'),y=alt.Y('low:Q',title=None,axis=None),y2='high:Q').properties(height=100),use_container_width=True)
    a,b,c=st.columns(3); a.metric('Duration',f'{duration:.1f}s'); b.metric('Notes',len(r['notes'])); c.metric('Tempo',f"{r['bpm']} BPM")
    a,b,c=st.columns(3); a.download_button('↓ MIDI',r['midi'],'sonata.mid',use_container_width=True); b.download_button('↓ WAV',r['audio'],'sonata.wav',use_container_width=True)
    if c.button('＋ Save track',use_container_width=True): st.session_state.library.append(r.copy()); st.toast('Saved to session library')
   with st.container(border=True):
    st.subheader('🎹 MIDI sequencer'); st.caption('Pitch classes present in the composition · keyboard visualization'); keyboard(r['notes']); st.caption('Actual note events • duration and pitch')
    if r['notes']:
     df=pd.DataFrame(r['notes']); df['note']=df.pitch.map(pm.note_number_to_name); df['class']=df.pitch%12
     st.altair_chart(alt.Chart(df).mark_bar(size=11,cornerRadius=3).encode(x=alt.X('start:Q',title='Seconds'),x2='end:Q',y=alt.Y('pitch:O',sort='descending',title='MIDI pitch'),color=alt.Color('class:N',scale=alt.Scale(range=['#a78bfa','#22d3ee','#f472b6','#fbbf24','#34d399','#818cf8']),legend=None),tooltip=['note','start','end','velocity']).properties(height=250).interactive(),use_container_width=True)
  else: st.info('Generate a track to activate the sound canvas.')
 st.caption('WAV uses a basic harmonic synthesizer; instrument selection changes MIDI playback programs, not WAV timbre.')
elif page.startswith('💿'):
 st.title('Your sound collection'); st.caption('Tracks saved during this browser session.')
 if not st.session_state.library: st.info('Save a track from the composition desk.')
 for i,r in enumerate(st.session_state.library):
  with st.container(border=True):
   st.subheader(f"{i+1:02} / {r['name']}"); player(r['audio']); a,b,c=st.columns(3); a.download_button('MIDI',r['midi'],f'track-{i}.mid',key=f'm{i}'); b.download_button('WAV',r['audio'],f'track-{i}.wav',key=f'w{i}');
   if c.button('Remove',key=f'd{i}'): st.session_state.library.pop(i); st.rerun()
elif page.startswith('🧠'):
 st.title('Model training lab'); st.caption('Train your own next-note prediction model.')
 a,b=st.columns([1,1]);
 with a:
  with st.container(border=True):
   uploads=st.file_uploader('Licensed MIDI dataset',type=['mid','midi'],accept_multiple_files=True); epochs=st.slider('Epochs',1,50,15); st.warning('Training replaces the existing local checkpoint.');
   if st.button('Start training',type='primary'):
    try:
     with st.spinner('Training neural network…'):
      with tempfile.TemporaryDirectory() as d:
       for j,f in enumerate(uploads): (pathlib.Path(d)/f'{j}.mid').write_bytes(f.getvalue())
       train(d if uploads else ROOT/'data',epochs)
     st.success('Training complete')
    except Exception as exc: st.error(str(exc))
 with b:
  tile('ARCHITECTURE','2-layer LSTM','#c4b5fd'); tile('VOCABULARY','129 tokens','#67e8f9'); tile('DEMO DATASET',str(len(list((ROOT/'data').glob('*.mid'))))+' MIDI files','#fbbf24')
else:
 st.title('Neural analytics'); st.caption('Measured training history and composition statistics.')
 if (ROOT/'history.json').exists():
  df=pd.DataFrame(json.loads((ROOT/'history.json').read_text())); cols=st.columns(3)
  for col,label,value,color in zip(cols,['EPOCHS','FINAL LOSS','VALIDATION LOSS'],[len(df),f"{df.loss.iloc[-1]:.3f}",f"{df.val_loss.iloc[-1]:.3f}" if 'val_loss' in df else 'N/A'],['#a78bfa','#34d399','#22d3ee']):
   with col: tile(label,value,color)
  fields=['loss']+(['val_loss'] if 'val_loss' in df else []); long=df.melt(id_vars='epoch',value_vars=fields,var_name='series',value_name='loss_value'); st.altair_chart(alt.Chart(long).mark_line(point=True,strokeWidth=3).encode(x='epoch:Q',y='loss_value:Q',color=alt.Color('series:N',scale=alt.Scale(range=['#a78bfa','#22d3ee'])),tooltip=['epoch','series','loss_value']).properties(height=300),use_container_width=True); st.dataframe(df,use_container_width=True)
  if 'val_accuracy' in df: st.line_chart(df,x='epoch',y='val_accuracy',color='#34d399')
 else: st.info('No training history yet.')
 r=st.session_state.get('result');
 if r and r['notes']:
  st.subheader('Pitch distribution'); df=pd.DataFrame(r['notes']); st.altair_chart(alt.Chart(df).mark_bar(color='#f472b6').encode(x='pitch:O',y='count()').properties(height=220),use_container_width=True)
