# VELUSE

The public Veluse marketing site. Static HTML, CSS, and JavaScript; no package installation, framework build, runtime styling service, web font, or external icon library is required.

Serve this directory as the site root. For example, with an existing Python installation:

```sh
python -m http.server 4173 --bind 127.0.0.1
```

Open `http://127.0.0.1:4173`. Deploy the root directory through the existing static hosting project. This change does not configure hosting or change DNS.

## Design and motion

The design preserves Veluse's original metallic ribbon V and indigo/cyan identity, with near-black navy surfaces, flowing SVG gradients, clear typography, and a quieter editorial hierarchy. Every logo uses `favicon.png`; the source favicon is unchanged. The hero has no status dot, technical badge, or decorative system labels. All assets are local; no artwork, code, fonts, or dependencies are loaded from the visual reference site.

- The original neural-network motif: 140 drifting desktop nodes (42 on mobile), proximity connections, firing pulses, brief node flashes, and pointer repulsion. Coordinates are neither stored nor transmitted.
- Five growth phases in a vertical, native-scroll narrative inspired by the reference site's horizontal numbered panels. Each phase brings its own drawing, scanning, and construction graphics into view. There are no phase-selection buttons.
- A pinned vertical rail on wide, tall screens; normal document flow on phones, short viewports, and with reduced motion. The page never intercepts wheel input or scrolls the browser programmatically.
- Native SVG folds drift vertically in Veluse's darker indigo palette, with the original firing neural network retained underneath.
- The first screen places the original logo in a gently floating obsidian and chrome sculpture, wrapped by indigo ribbons. Its motion obeys the same pause, hidden-tab, and reduced-motion controls.
- Animated acquisition schematics and an explicitly illustrative OS workflow.
- Progressive scroll reveals; content remains visible without JavaScript.
- Motion pause/play control, reduced-motion preferences, and background pausing.
- Mobile navigation, native modal dialogs, keyboard focus return, and required form fields.

All visual assets are local. `assets/social-card.svg` is the editable source for the PNG social image; the PNG ships pre-rendered.

## Intake contract

The existing Google Apps Script endpoint is unchanged, including its POST method, `no-cors` mode, text/plain body, and `name`, `organization`, `email`, `revenue`, `bottlenecks` fields. Requests have a 15-second timeout. A rejected request retains the entered details and permits retry. Pending and completed submissions are protected against duplicate sends in the current page session.

An opaque `no-cors` response does **not** verify lead persistence. The confirmation message explicitly says that receipt cannot be confirmed and provides the existing business email. No production form submission was made during verification.

The existing policy and terms text is preserved verbatim in `assets/privacy.txt` and `assets/terms.txt`. This change does not validate the pre-existing policies' legal, security, or compliance assertions.

## Checks

With Node.js available:

```sh
node --check assets/site.js
node --check assets/neural.js
node --check assets/protocol.js
node --test tests/*.test.cjs
git diff --check
```

Eighteen isolated checks exercise the intake contract, truthful opaque-response status, rejection/retry, invalid input, duplicate submissions, motion pause persistence, reduced-motion preference, renderer resolution caps, cancellation/resumption of the neural loop, forward/reverse story progression, phase transitions, mobile flow, and coalescing scroll updates into one requested frame. They never make a network request.

Browser verification covers mobile navigation, scrolling through the narrative, required-field validation, Escape closing and focus return, legal dialogs, motion control, and layouts at 320, 375, 390, 768, 1024, and 1440 pixels. Backend delivery and production deployment require separate verification.
