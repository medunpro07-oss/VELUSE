# VELUSE

The public Veluse marketing site. Static HTML, CSS, and JavaScript; no package installation, framework build, runtime styling service, web font, or external icon library is required.

Serve this directory as the site root. For example, with an existing Python installation:

```sh
python -m http.server 4173 --bind 127.0.0.1
```

Open `http://127.0.0.1:4173`. Deploy the root directory through the existing static hosting project. This change does not configure hosting or change DNS.

## Design and motion

The design keeps Veluse's dark surfaces, indigo/cyan accents, engineering motif, and Precision Revenue Architecture positioning. Warm neutral content sections, editorial typography, and restrained spacing make the services easier to scan.

- SVG acquisition map with animated orbits and signal paths.
- Five selectable growth phases with a transitioning layered illustration.
- Lightweight service animations and an explicitly illustrative OS workspace.
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
node --test tests/contact.test.cjs
git diff --check
```

The seven isolated checks exercise the intake contract, truthful opaque-response status, rejection/retry, invalid input, duplicate submissions, motion pause persistence, and reduced-motion preference. They never make a network request.

Browser verification covers the mobile navigation, all five phase choices, required-field validation, Escape closing and focus return, both legal dialogs, motion control, and layouts at 320, 375, 390, 768, 1024, and 1440 pixels. Backend delivery and production deployment require separate verification.
