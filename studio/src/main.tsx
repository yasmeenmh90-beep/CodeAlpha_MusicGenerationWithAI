import {useEffect, useRef, useState} from 'react';
import {createRoot} from 'react-dom/client';
import Analytics from './Analytics';
import Arrangement from './Arrangement';
import Beat from './Beat';
import GlobalDeck from './GlobalDeck';
import Instruments from './Instruments';
import Library from './Library';
import Piano from './Piano';
import Player from './Player';
import StudioHome from './StudioHome';
import Training from './Training';
import './workstation.css';
import './workspaces.css';

const groups = [
  {name: 'Workspace', items: [['Studio', '⌂'], ['AI Composer', '♫'], ['Arrangement', '▤']]},
  {name: 'Performance', items: [['Piano Studio', '▥'], ['Beat Maker', '▦'], ['Mixer', '☷'], ['Instruments', '♪']]},
  {name: 'Collection & insights', items: [['Music Library', '▤'], ['Visualizer', '◉'], ['Training', '◈'], ['Analytics', '⌁']]},
];
const themes = ['graphite', 'aurora', 'gold', 'cyber', 'ocean', 'crimson', 'arctic'];

function App() {
  const [page, setPage] = useState('Studio');
  const [bpm, setBpm] = useState(128);
  const [temperature, setTemperature] = useState(.9);
  const [motion, setMotion] = useState(() => localStorage.getItem('sonata-motion') !== 'off');
  const [theme, setTheme] = useState(() => {
    const saved = localStorage.getItem('sonata-theme');
    return saved && themes.includes(saved) ? saved : 'graphite';
  });
  const [compact, setCompact] = useState(false);
  const [palette, setPalette] = useState(false);
  const main = useRef<HTMLElement>(null);
  const paletteButton = useRef<HTMLButtonElement>(null);
  const closePaletteButton = useRef<HTMLButtonElement>(null);
  const drumWorkspace = page === 'Beat Maker' || page === 'Mixer';

  function go(name: string) {
    setPage(name);
    setPalette(false);
  }

  useEffect(() => { localStorage.setItem('sonata-theme', theme); }, [theme]);
  useEffect(() => { localStorage.setItem('sonata-motion', motion ? 'on' : 'off'); }, [motion]);
  useEffect(() => { main.current?.scrollTo(0, 0); }, [page]);
  useEffect(() => { if (palette) closePaletteButton.current?.focus(); }, [palette]);
  useEffect(() => {
    function key(event: KeyboardEvent) {
      if ((event.metaKey || event.ctrlKey) && event.key.toLowerCase() === 'k') {
        event.preventDefault();
        if (palette) paletteButton.current?.focus();
        setPalette(!palette);
      }
      if (event.key === 'Escape' && palette) {
        setPalette(false);
        paletteButton.current?.focus();
      }
    }
    window.addEventListener('keydown', key);
    return () => window.removeEventListener('keydown', key);
  }, [palette]);

  return (
    <div data-theme={theme} className={`workstation ${motion ? 'motion' : 'still'}${compact ? ' compact-nav' : ''}`}>
      <header className="work-top">
        <div className="brand">
          <div className="brand-wave" aria-hidden="true">{[12, 23, 35, 19, 30, 12].map((height, i) => <i key={i} style={{height}}/>)}</div>
          <div>Sonata<span>AI</span><small>STUDIO</small></div>
        </div>
        <button onClick={() => setCompact(value => !value)} aria-label="Toggle sidebar" aria-pressed={compact}>☰</button>
        <strong className="shell-page" aria-live="polite">{page}</strong>
        <div className="shell-actions">
          {drumWorkspace && <div className="shell-settings"><label>BPM<input type="number" min="30" max="240" value={bpm} onChange={event => setBpm(Math.max(30, Math.min(240, +event.target.value)))}/></label></div>}
          <button ref={paletteButton} aria-label="Open workspace switcher" aria-haspopup="dialog" aria-expanded={palette} onClick={() => setPalette(true)}>⌘ K</button>
          <select aria-label="Studio theme" value={theme} onChange={event => setTheme(event.target.value)}>
            {themes.map(option => <option key={option}>{option}</option>)}
          </select>
          <button aria-pressed={motion} onClick={() => setMotion(value => !value)}>Motion {motion ? 'on' : 'off'}</button>
        </div>
      </header>
      <nav className="work-side" aria-label="Workspaces">
        {groups.map(group => (
          <div className="nav-group" key={group.name}>
            <small>{group.name}</small>
            {group.items.map(([name, icon]) => (
              <button key={name} title={name} aria-label={name} aria-current={page === name ? 'page' : undefined} className={page === name ? 'chosen' : ''} onClick={() => go(name)}>
                <span aria-hidden="true">{icon}</span><b>{name}</b>
              </button>
            ))}
          </div>
        ))}
      </nav>
      <main ref={main} className="work-main">
        {palette && (
          <div className="workspace-palette" role="dialog" aria-label="Navigate">
            <button ref={closePaletteButton} onClick={() => {setPalette(false); paletteButton.current?.focus();}}>Close ×</button>
            {groups.flatMap(group => group.items).map(([name, icon]) => <button key={name} onClick={() => go(name)}><span aria-hidden="true">{icon}</span> {name}</button>)}
          </div>
        )}
        {page === 'Studio' && <StudioHome go={go} bpm={bpm}/>}
        {drumWorkspace && <Beat bpm={bpm} mixer={page === 'Mixer'} standalone={page === 'Beat Maker'}/>}
        {page === 'AI Composer' && <Player bpm={bpm} temperature={temperature} onBpm={setBpm} onTemperature={setTemperature} standalone/>}
        {page === 'Piano Studio' && <Piano standalone/>}
        {page === 'Music Library' && <Library onCreate={() => go('AI Composer')}/>}
        {page === 'Analytics' && <Analytics/>}
        {page === 'Training' && <Training/>}
        {page === 'Arrangement' && <Arrangement/>}
        {page === 'Instruments' && <Instruments/>}
        {page === 'Visualizer' && <GlobalDeck visual/>}
      </main>
    </div>
  );
}

createRoot(document.getElementById('root')!).render(<App/>);
