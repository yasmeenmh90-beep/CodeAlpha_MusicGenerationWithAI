import assert from 'node:assert/strict';
import {readFile} from 'node:fs/promises';
import {chromium} from 'playwright';

const studio = process.env.STUDIO_URL || 'http://127.0.0.1:5173';
const api = process.env.VITE_API_URL || 'http://localhost:8000';

const workspaces = ['Studio', 'AI Composer', 'Arrangement', 'Piano Studio', 'Beat Maker', 'Mixer',
  'Instruments', 'Music Library', 'Visualizer', 'Training', 'Analytics'];

(async () => {
  const base = api;
  for (const path of ['/health', '/training/history']) {
    const response = await fetch(base + path);
    if (!response.ok) throw new Error(path + ': ' + response.status);
    const body = await response.json();
    if (path === '/health') assert.equal(body.model_ready, true);
    else assert(body.original.length > 0, 'Baseline training history is empty');
  }
  const browser = await chromium.launch({
    executablePath: process.env.CHROME_PATH, headless: true,
  });
  try {
    const context = await browser.newContext({ viewport: { width: 1440, height: 900 } });
    const page = await context.newPage();
    const errors = [];
    page.on('response', response => { if (response.status() >= 400) errors.push(response.status() + ' ' + response.url()); });
    page.on('pageerror', error => errors.push(error.message));
    page.on('console', message => { if (message.type() === 'error') errors.push(message.text()); });
    page.setDefaultTimeout(8000);
    await page.goto(studio);
    await page.getByRole('heading', {name: 'Session overview'}).waitFor();
    const go = async name => {
      await page.getByRole('navigation').getByRole('button', { name, exact: true }).click();
      await page.locator('main > section').waitFor();
      assert.equal(await page.locator('.shell-page').textContent(), name);
    };
    const checkLayout = async (name, width) => {
      for (const selector of ['html', '.work-top', 'main']) {
        const overflow = await page.locator(selector).evaluate(el => el.scrollWidth > el.clientWidth + 2);
        assert(!overflow, name + ' overflows ' + selector + ' at ' + width + 'px');
      }
    };

    await page.getByRole('button', {name: 'Open workspace switcher'}).press('Control+k');
    await page.getByRole('dialog', {name: 'Navigate'}).waitFor();
    await page.keyboard.press('Escape');
    await page.getByRole('dialog', {name: 'Navigate'}).waitFor({state: 'hidden'});
    const theme = page.getByLabel('Studio theme');
    const shell = page.locator('.workstation');
    await page.getByRole('button', {name: 'Motion on'}).click();
    const accents = new Set();
    for (const name of ['aurora', 'gold', 'cyber', 'ocean', 'crimson', 'arctic']) {
      await theme.selectOption(name);
      assert.equal(await shell.getAttribute('data-theme'), name);
      accents.add(await page.locator('.primary').first().evaluate(el => getComputedStyle(el).backgroundColor));
    }
    assert.equal(accents.size, 6);
    assert.equal(await page.getByRole('button', {name: 'Motion off'}).evaluate(el => getComputedStyle(el).transitionDuration), '0s');
    await page.reload();
    assert.equal(await theme.inputValue(), 'arctic');
    await page.getByRole('button', {name: 'Motion off'}).click();
    assert.equal(await page.getByRole('button', {name: 'Motion on'}).getAttribute('aria-pressed'), 'true');
    console.log('Verified workspace switcher, six theme accents and motion persistence');
    await theme.selectOption('graphite');
    await page.emulateMedia({reducedMotion: 'reduce'});
    assert.equal(await page.getByRole('button', {name: 'Motion on'}).evaluate(el => getComputedStyle(el).transitionDuration), '0s');
    await page.emulateMedia({reducedMotion: 'no-preference'});
    await go('AI Composer');
    await page.getByRole('button', { name: 'Generate AI music' }).click();
    await page.getByText('Your generated composition', { exact: true }).waitFor({ timeout: 45000 });
    await page.getByRole('button', { name: '▶ Play', exact: true }).click();
    await page.getByRole('button', { name: 'Ⅱ Pause', exact: true }).waitFor();
    await checkLayout('AI Composer', 1440);
    await go('Arrangement');
    await page.getByLabel('Source audio').selectOption({ index: 1 });
    await page.getByRole('button', { name: 'Add clip' }).click();
    await page.getByRole('button', { name: 'Play arrangement' }).click();
    await page.getByText('● PLAYING', { exact: true }).waitFor();
    await checkLayout('Arrangement', 1440);
    await go('Piano Studio');
    await page.getByLabel('Octave').selectOption('7');
    assert.equal(await page.locator('.piano-key').count(), 32);
    await page.getByRole('button', {name: 'Record'}).click();
    await page.keyboard.press('a');
    await page.getByRole('button', {name: 'C8', exact: true}).press('Space');
    await page.getByRole('button', {name: 'G9', exact: true}).press('Space');
    await page.getByRole('button', {name: 'Stop'}).click();
    assert.deepEqual(await page.getByLabel('Pitch', {exact: true}).evaluateAll(inputs => inputs.map(input => +input.value)), [96, 108, 127]);
    for (const name of ['C7', 'C8', 'G9']) {
      assert.equal(await page.locator('.roll-lane i[title^="' + name + ' ·"]').count(), 1);
    }
    await page.getByLabel('Pitch', {exact: true}).first().fill('0');
    assert.equal(await page.locator('.roll-lane i[title^="C-1 ·"]').count(), 1);
    const download = page.waitForEvent('download');
    await page.getByRole('button', {name: 'MIDI'}).click();
    const midi = await readFile(await (await download).path());
    assert.equal(midi.toString('ascii', 0, 4), 'MThd');
    const pitches = [];
    for (let offset = 22; offset < midi.length;) {
      while (midi[offset++] & 0x80) { /* skip delta time */ }
      const status = midi[offset++];
      if (status === 0xff) {
        offset++;
        const size = midi[offset++];
        offset += size;
      } else {
        assert(midi[offset] <= 127 && midi[offset + 1] <= 127);
        if (status === 0x90) pitches.push(midi[offset]);
        else assert.equal(status, 0x80);
        offset += 2;
      }
    }
    assert.deepEqual(pitches, [0, 108, 127]);
    await checkLayout('Piano Studio', 1440);
    await go('Beat Maker');
    await page.getByRole('button', { name: 'Kick step 2' }).click();
    await page.getByRole('button', { name: 'Play groove' }).click();
    await page.locator('.rp-current').first().waitFor();
    await checkLayout('Beat Maker', 1440);
    await go('Mixer');
    await page.getByRole('button', { name: 'Stop', exact: false }).waitFor();
    await page.waitForTimeout(350);
    await checkLayout('Mixer', 1440);
    await go('Instruments');
    await page.getByRole('button', { name: /Glass Bell/ }).click();
    await page.getByRole('button', { name: 'C4', exact: true }).click();
    await page.locator('.inst-monitor').getByText('C4', { exact: true }).waitFor();
    await checkLayout('Instruments', 1440);
    await go('Music Library');
    await page.getByRole('button', { name: 'Toggle favorite' }).click();
    await page.getByRole('button', { name: 'Favorites' }).click();
    await page.locator('.collection-cover button').click();
    await page.getByRole('button', { name: 'Pause', exact: true }).waitFor();
    await checkLayout('Music Library', 1440);
    await go('Visualizer');
    await page.getByRole('button', { name: 'Waveform' }).click();
    await page.getByLabel('Select library track').selectOption({ index: 1 });
    await page.getByRole('button', { name: 'Play', exact: true }).click();
    await page.getByText('● LIVE SIGNAL').waitFor();
    await page.getByText('Sound shaping · Effects rack').click();
    await checkLayout('Visualizer', 1440);
    await go('Training');
    await page.getByText('Backend connected', {exact: true}).waitFor();
    await page.getByRole('heading', {name: 'Epoch history'}).waitFor();
    if (process.env.TRAINING_SCREENSHOT) await page.screenshot({path: process.env.TRAINING_SCREENSHOT});
    await go('Analytics');
    await page.getByText('Model history connected', {exact: true}).waitFor();
    await go('Studio');
    await page.getByRole('heading', {name: 'Session overview'}).waitFor();
    for (const width of [1440, 1024, 768, 390, 320]) {
      await page.setViewportSize({width, height: 900});
      for (const name of workspaces) {
        await go(name);
        await checkLayout(name, width);
      }
      console.log('Checked all 11 workspaces at ' + width + 'px');
    }
    if (errors.length) throw Error(errors.join('\n'));
    console.log('Studio browser regression passed');
  } finally { await browser.close(); }
})().catch(error => { console.error(error); process.exitCode = 1; });
