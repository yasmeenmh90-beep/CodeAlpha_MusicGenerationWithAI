import {load} from './Library';

const tools = [
  ['AI Composer', 'Generate MIDI and WAV', 'violet', '∿'],
  ['Arrangement', 'Sequence library audio', 'cyan', '▤'],
  ['Piano Studio', 'Play and record MIDI', 'pink', '▥'],
  ['Beat Maker', 'Program drum patterns', 'amber', '▦'],
  ['Mixer', 'Balance drum channels', 'blue', '☷'],
  ['Instruments', 'Audition synth voices', 'violet', '△'],
  ['Music Library', 'Manage saved audio', 'cyan', '♫'],
  ['Visualizer', 'Inspect audio and shape effects', 'pink', '◉'],
  ['Training', 'Inspect model checkpoints', 'amber', '◈'],
  ['Analytics', 'Review composition statistics', 'blue', '⌁'],
];

export default function StudioHome({go, bpm}: {go: (name: string) => void; bpm: number}) {
  const tracks = load();
  const seconds = tracks.reduce((sum, track) => sum + track.duration, 0);
  const duration = Math.floor(seconds / 60) + ':' + String(Math.floor(seconds % 60)).padStart(2, '0');

  return (
    <section className="studio-home">
      <header className="session-heading">
        <div><h1>Session overview</h1><p>SonataAI Studio</p></div>
        <button className="primary" onClick={() => go('AI Composer')}>+ New composition</button>
      </header>
      <div className="session-metrics">
        {[[bpm, 'Session BPM'], [tracks.length, 'Saved tracks'], [duration, 'Total audio'], [tracks.filter(track => track.favorite).length, 'Favorites']].map(([value, label]) => (
          <div key={label}><small>{label}</small><strong>{value}</strong></div>
        ))}
      </div>
      <div className="session-grid">
        <section className="panel">
          <h2>Workspaces</h2>
          <div className="session-tools">
            {tools.map(([name, description, color, icon]) => (
              <button key={name} className={color} onClick={() => go(name)}>
                <i aria-hidden="true">{icon}</i><span><strong>{name}</strong><small>{description}</small></span>
              </button>
            ))}
          </div>
        </section>
        <section className="panel">
          <header className="session-recent-header"><h2>Recent compositions</h2><button onClick={() => go('Music Library')}>Library →</button></header>
          {tracks.length ? (
            <ul className="session-tracks">
              {tracks.slice(0, 8).map(track => (
                <li key={track.id}><button onClick={() => go('Music Library')}><span>{track.name}<small>{track.genre} · {track.bpm} BPM</small></span><small>{track.duration.toFixed(1)}s</small></button></li>
              ))}
            </ul>
          ) : <p className="empty">Generated compositions will appear here.</p>}
        </section>
      </div>
    </section>
  );
}
