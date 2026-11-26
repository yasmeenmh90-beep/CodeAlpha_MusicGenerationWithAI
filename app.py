import streamlit as st
import tempfile, pathlib, json
from music import ROOT,generate,export,train
st.set_page_config(page_title='SonataAI',page_icon='🎹',layout='wide')
st.title('SonataAI / Music Studio'); st.caption('Neural composition · LSTM research workspace')
a,b,c=st.tabs(['Compose','Training studio','Analytics'])
with a:
 left,right=st.columns([1,2]);
 with left:
  bpm=st.slider('Tempo',60,180,100); temp=st.slider('Creativity',.1,2.,.9); length=st.slider('Sequence steps',32,512,128); instrument=st.selectbox('MIDI instrument',['Piano','Electric piano','Guitar','Violin']); seed=st.number_input('Random seed',0,100000,42)
  if st.button('Generate composition',type='primary'):
   if not (ROOT/'model.pt').exists(): st.error('Train a model first.')
   else:
    m,notes=generate(length,temp,bpm,[0,4,24,40][['Piano','Electric piano','Guitar','Violin'].index(instrument)],seed)
    with tempfile.TemporaryDirectory() as d:
     p=pathlib.Path(d)/'composition'; export(m,p); st.session_state['result']=(p.with_suffix('.mid').read_bytes(),p.with_suffix('.wav').read_bytes(),notes)
 with right:
  if 'result' in st.session_state:
   midi,audio,notes=st.session_state.result; st.audio(audio,format='audio/wav'); st.line_chart([n if n<128 else None for n in notes]); st.download_button('Export MIDI',midi,'composition.mid'); st.download_button('Export WAV',audio,'composition.wav')
  else: st.info('Generate your first composition.')
with b:
 uploads=st.file_uploader('Upload licensed MIDI files',type=['mid','midi'],accept_multiple_files=True); epochs=st.slider('Training epochs',1,50,15)
 if st.button('Train model'):
  try:
   with st.spinner('Training LSTM…'):
    with tempfile.TemporaryDirectory() as d:
     for j,f in enumerate(uploads): (pathlib.Path(d)/f'{j}.mid').write_bytes(f.getvalue())
     train(d if uploads else ROOT/'data',epochs)
   st.success('Training complete')
  except Exception as e: st.error(str(e))
with c:
 if (ROOT/'history.json').exists():
  rows=json.loads((ROOT/'history.json').read_text()); st.line_chart(rows,x='epoch',y=['loss']+(['val_loss'] if 'val_loss' in rows[0] else [])); st.dataframe(rows)
 else: st.info('Train to see metrics.')
