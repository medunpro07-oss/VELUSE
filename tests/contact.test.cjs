const test = require('node:test');
const assert = require('node:assert/strict');
const vm = require('node:vm');
const fs = require('node:fs');
const path = require('node:path');
const source = fs.readFileSync(path.join(__dirname, '../assets/site.js'), 'utf8');

// Isolate the intake state machine: no browser, credentials, or real requests.
function setup({ fetchImpl = async () => ({}), valid = true, reduced = false, values } = {}) {
  const elements = new Map();
  function element(selector) {
    if (!elements.has(selector)) {
      const classes = new Set();
      elements.set(selector, {
        textContent: '', disabled: false, events: {}, attributes: {},
        classList: { toggle(name, on) { on ? classes.add(name) : classes.delete(name); }, remove(name) { classes.delete(name); }, contains(name) { return classes.has(name); } },
        setAttribute(key, value) { this.attributes[key] = value; },
        addEventListener(name, callback) { this.events[name] = callback; },
        querySelectorAll() { return []; },
        reportValidity() { return valid; },
        reset() { this.resetCalled = true; }
      });
    }
    return elements.get(selector);
  }
  const requests = [];
  const docEvents = {};
  const document = {
    hidden: false, documentElement: element('html'),
    querySelector: element, querySelectorAll() { return []; },
    addEventListener(name, callback) { docEvents[name] = callback; }
  };
  const data = values || { name: ' Alex ', organization: ' Example ', email: ' alex@example.com ', revenue: '$20K - $50K / mo', bottlenecks: ' Improve follow-up. ' };
  const context = {
    document, window: { matchMedia: () => ({ matches: reduced, addEventListener() {} }) },
    FormData: class { constructor() { return Object.entries(data); } },
    AbortSignal, Date,
    fetch: async (...args) => { requests.push(args); return fetchImpl(...args); }
  };
  vm.runInNewContext(source, context);
  return {
    element, requests, document, docEvents,
    send: () => element('#contact-form').events.submit({ preventDefault() {} })
  };
}

test('valid request preserves endpoint, field names, trimming, and no-cors contract', async () => {
  const app = setup();
  await app.send();
  assert.equal(app.requests.length, 1);
  const [endpoint, options] = app.requests[0];
  assert.match(endpoint, /^https:\/\/script.google.com\/macros\/s\/.+\/exec$/);
  assert.equal(options.method, 'POST');
  assert.equal(options.mode, 'no-cors');
  assert.deepEqual(JSON.parse(options.body), { name: 'Alex', organization: 'Example', email: 'alex@example.com', revenue: '$20K - $50K / mo', bottlenecks: 'Improve follow-up.' });
  assert.ok(options.signal);
});
test('opaque response explicitly leaves receipt unconfirmed', async () => {
  const app = setup();
  await app.send();
  assert.match(app.element('#form-status').textContent, /receipt cannot be confirmed/);
  assert.equal(app.element('#contact-form').resetCalled, true);
  assert.equal(app.element('#submit-contact').disabled, true);
});
test('network rejection permits retry and keeps entered details', async () => {
  const app = setup({ fetchImpl: async () => { throw new Error('Offline'); } });
  await app.send();
  assert.equal(app.element('#submit-contact').disabled, false);
  assert.equal(app.element('#submit-contact').textContent, 'Try again');
  assert.match(app.element('#form-status').textContent, /couldn’t confirm delivery/);
  assert.equal(app.element('#contact-form').resetCalled, undefined);
});
test('invalid and whitespace-only entries never make a request', async () => {
  const invalid = setup({ valid: false });
  await invalid.send();
  assert.equal(invalid.requests.length, 0);
  const blank = setup({ values: { name: '  ', organization: 'Example', email: 'alex@example.com', revenue: 'test', bottlenecks: 'test' } });
  await blank.send();
  assert.equal(blank.requests.length, 0);
});
test('repeated submission while pending makes only one request', async () => {
  let finish;
  const app = setup({ fetchImpl: () => new Promise(resolve => { finish = resolve; }) });
  const pending = app.send();
  await app.send();
  assert.equal(app.requests.length, 1);
  finish({});
  await pending;
});
test('manual pause survives background and foreground transitions', () => {
  const app = setup();
  app.element('.motion-toggle').events.click();
  app.document.hidden = true;
  app.docEvents.visibilitychange();
  app.document.hidden = false;
  app.docEvents.visibilitychange();
  assert.equal(app.element('html').classList.contains('motion-paused'), true);
  assert.equal(app.element('.motion-toggle').attributes['aria-pressed'], 'true');
});
test('reduced-motion preference pauses loops and disables motion control', () => {
  const app = setup({ reduced: true });
  assert.equal(app.element('html').classList.contains('motion-paused'), true);
  assert.equal(app.element('.motion-toggle').disabled, true);
  assert.equal(app.element('.motion-toggle').textContent, 'Motion reduced');
});
