const test = require('node:test');
const assert = require('node:assert/strict');
const fs = require('node:fs');
const vm = require('node:vm');
const path = require('node:path');
const source = fs.readFileSync(path.join(__dirname, '../assets/neural.js'), 'utf8');

function renderer({ reduced = false } = {}) {
  const frames = new Map();
  const listeners = {};
  let observer;
  let paused = false;
  let nextId = 0;
  let draws = 0;
  const context = new Proxy({}, { get: (_, key) => key === 'clearRect' ? () => { draws++; } : () => {} });
  const canvas = { getContext: () => context };
  const document = {
    hidden: false,
    documentElement: { classList: { contains: () => paused } },
    querySelector: () => canvas,
    addEventListener: (name, callback) => { listeners[name] = callback; }
  };
  const window = {
    innerWidth: 1200, innerHeight: 800, devicePixelRatio: 3,
    matchMedia: () => ({ matches: reduced, addEventListener() {} }),
    addEventListener() {}
  };
  vm.runInNewContext(source, {
    document, window,
    MutationObserver: class { constructor(callback) { observer = callback; } observe() {} },
    requestAnimationFrame(callback) { const id = ++nextId; frames.set(id, callback); return id; },
    cancelAnimationFrame(id) { frames.delete(id); }
  });
  return {
    frames, canvas, document, listeners,
    draws: () => draws,
    pause(value) { paused = value; observer(); },
    tick(time) { const [id, callback] = frames.entries().next().value; frames.delete(id); callback(time); }
  };
}
test('backing resolution is capped at 2x and only one frame is queued', () => {
  const app = renderer();
  assert.equal(app.canvas.width, 2400);
  assert.equal(app.canvas.height, 1600);
  assert.equal(app.frames.size, 1);
  app.tick(100);
  app.tick(116);
  assert.equal(app.frames.size, 1);
  assert.ok(app.draws() >= 3);
});
test('manual pause cancels animation and resume does not duplicate its loop', () => {
  const app = renderer();
  app.pause(true);
  assert.equal(app.frames.size, 0);
  app.pause(false);
  app.pause(false);
  assert.equal(app.frames.size, 1);
});
test('backgrounding cancels the loop and foregrounding starts one frame', () => {
  const app = renderer();
  app.document.hidden = true;
  app.listeners.visibilitychange();
  assert.equal(app.frames.size, 0);
  app.document.hidden = false;
  app.listeners.visibilitychange();
  assert.equal(app.frames.size, 1);
});
test('reduced motion renders a static neural network without an animation loop', () => {
  const app = renderer({ reduced: true });
  assert.equal(app.frames.size, 0);
  assert.ok(app.draws() >= 1);
});
