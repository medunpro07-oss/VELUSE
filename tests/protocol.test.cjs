const test = require('node:test');
const assert = require('node:assert/strict');
const fs = require('node:fs');
const path = require('node:path');
const vm = require('node:vm');
const source = fs.readFileSync(path.join(__dirname, '../assets/protocol.js'), 'utf8');

function setup({ wide = true, reduced = false, height = 900 } = {}) {
  const frames = new Map();
  const events = {};
  const documentEvents = {};
  let nextId = 0;
  let storyTop = 0;
  let flowScroll = 0;
  let mutation;
  function element() {
    const classes = new Set();
    return {
      dataset: {}, textContent: '',
      style: { values: {}, transform: '', setProperty(name, value) { this.values[name] = value; } },
      classList: { toggle(name, on) { on ? classes.add(name) : classes.delete(name); }, contains(name) { return classes.has(name); } }
    };
  }
  const stage = element();
  stage.getBoundingClientRect = () => ({ bottom: 210 });
  const track = element();
  const current = element();
  const count = element();
  const chapters = ['Foundation', 'Awareness', 'Acquisition', 'Nurturing', 'Scaling'].map((name, index) => ({
    ...element(), offsetTop: index * 560,
    querySelector: () => ({ textContent: name }),
    getBoundingClientRect: () => ({ top: index * 500 - flowScroll, height: 500 })
  }));
  const scenes = chapters.map(() => element());
  const story = element();
  story.getBoundingClientRect = () => ({ top: storyTop, height: 3240 });
  story.querySelector = selector => ({ '.story-stage': stage, '.story-track': track, '.story-current': current, '.story-count': count })[selector];
  story.querySelectorAll = selector => selector === '[data-chapter]' ? chapters : scenes;
  const wideMedia = { matches: wide, addEventListener() {} };
  const reducedMedia = { matches: reduced, addEventListener() {} };
  const window = {
    innerHeight: height, scrollY: 0,
    matchMedia: query => query.includes('min-width') ? wideMedia : reducedMedia,
    addEventListener(name, callback) { events[name] = callback; }
  };
  const document = {
    hidden: false, documentElement: element(), querySelector: () => story,
    addEventListener(name, callback) { documentEvents[name] = callback; }
  };
  vm.runInNewContext(source, {
    window, document,
    MutationObserver: class { constructor(callback) { mutation = callback; } observe() {} },
    requestAnimationFrame(callback) { const id = ++nextId; frames.set(id, callback); return id; },
    cancelAnimationFrame(id) { frames.delete(id); }
  });
  function flush() {
    const entry = frames.entries().next().value;
    if (!entry) return;
    frames.delete(entry[0]);
    entry[1]();
  }
  flush();
  return {
    story, track, stage, current, count, chapters, scenes, window, document, frames, events, documentEvents, flush, wideMedia,
    move(top) { storyTop = top; window.scrollY = -top; events.scroll(); flush(); },
    flow(scroll) { flowScroll = scroll; events.scroll(); flush(); },
    pause(on) { document.documentElement.classList.toggle('motion-paused', on); mutation(); flush(); }
  };
}

test('vertical sequence reaches every chapter and reverses with native scroll', () => {
  const app = setup();
  assert.equal(app.story.dataset.mode, 'pinned');
  for (let index = 0; index < 5; index++) {
    app.move(-585 * index);
    assert.equal(app.story.dataset.active, String(index));
    assert.equal(app.track.style.transform, `translate3d(0, ${-560 * index}px, 0)`);
    assert.equal(app.chapters.filter(item => item.classList.contains('active')).length, 1);
    assert.equal(app.scenes.filter(item => item.classList.contains('active')).length, 1);
  }
  app.move(-585);
  assert.equal(app.current.textContent, 'Awareness');
  assert.equal(app.count.textContent, '02 / 05');
});
test('phase switches while the next chapter enters, rather than leaving it dim', () => {
  const app = setup();
  app.move(-360);
  assert.equal(app.story.dataset.active, '1');
  assert.ok(Number(app.stage.style.values['--phase-progress']) < 0.2);
});
test('scroll bursts coalesce into one frame and stop after rendering', () => {
  const app = setup();
  for (let i = 0; i < 20; i++) app.events.scroll();
  assert.equal(app.frames.size, 1);
  app.flush();
  assert.equal(app.frames.size, 0);
});
test('mobile and short viewports use normal document flow', () => {
  for (const config of [{ wide: false }, { height: 600 }]) {
    const app = setup(config);
    app.flow(850);
    assert.equal(app.story.dataset.mode, 'flow');
    assert.equal(app.track.style.transform, '');
    assert.equal(app.story.dataset.active, '2');
    assert.equal(app.chapters.length, 5);
  }
});
test('reduced motion keeps all chapters in flow with fully drawn graphics', () => {
  const app = setup({ reduced: true });
  assert.equal(app.story.dataset.mode, 'flow');
  assert.equal(app.stage.style.values['--draw'], '1');
  assert.equal(app.stage.style.values['--phase-progress'], '1');
  assert.equal(app.frames.size, 0);
});
test('manual pause stops decorative progress while leaving scroll navigation usable', () => {
  const app = setup();
  app.pause(true);
  app.move(-1170);
  assert.equal(app.story.dataset.active, '2');
  assert.equal(app.stage.style.values['--draw'], '1');
  app.pause(false);
  assert.ok(Number(app.stage.style.values['--draw']) < 1);
});
test('backgrounding cancels pending work and foregrounding schedules one update', () => {
  const app = setup();
  app.events.scroll();
  app.document.hidden = true;
  app.documentEvents.visibilitychange();
  assert.equal(app.frames.size, 0);
  app.document.hidden = false;
  app.documentEvents.visibilitychange();
  assert.equal(app.frames.size, 1);
});
