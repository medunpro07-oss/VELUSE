'use strict';

// Preserve the existing intake destination and payload contract.
const intakeEndpoint = 'https://script.google.com/macros/s/AKfycbyuWTgY13IwxJSct1U7oqo8DW1W6WnNpvNgaOix8g_G-7toEya-Kd_tS-XrFkZjT23YZQ/exec';
const reducedMotion = window.matchMedia('(prefers-reduced-motion: reduce)');
const menuButton = document.querySelector('.menu-toggle');
const navigation = document.querySelector('#primary-nav');
function closeMenu() {
  menuButton.setAttribute('aria-expanded', 'false');
  menuButton.setAttribute('aria-label', 'Open navigation');
  navigation.classList.remove('open');
}
menuButton.addEventListener('click', () => {
  const open = menuButton.getAttribute('aria-expanded') !== 'true';
  menuButton.setAttribute('aria-expanded', String(open));
  menuButton.setAttribute('aria-label', open ? 'Close navigation' : 'Open navigation');
  navigation.classList.toggle('open', open);
});
navigation.querySelectorAll('a').forEach(link => link.addEventListener('click', closeMenu));
document.addEventListener('keydown', event => { if (event.key === 'Escape') closeMenu(); });
window.matchMedia('(min-width: 761px)').addEventListener('change', closeMenu);

// Content stays visible when JavaScript or IntersectionObserver is unavailable.
if ('IntersectionObserver' in window && !reducedMotion.matches) {
  const observer = new IntersectionObserver(entries => {
    entries.forEach(entry => {
      if (entry.isIntersecting) {
        entry.target.classList.remove('pending');
        observer.unobserve(entry.target);
      }
    });
  }, { threshold: 0.08 });
  document.querySelectorAll('.reveal').forEach(element => {
    if (element.getBoundingClientRect().top > window.innerHeight) {
      element.classList.add('pending');
      observer.observe(element);
    }
  });
  document.documentElement.classList.add('motion-ready');
}
const motionButton = document.querySelector('.motion-toggle');
let userPausedMotion = false;
function updateMotion() {
  const paused = userPausedMotion || reducedMotion.matches;
  document.documentElement.classList.toggle('motion-paused', paused || document.hidden);
  motionButton.disabled = reducedMotion.matches;
  motionButton.setAttribute('aria-pressed', String(paused));
  motionButton.textContent = reducedMotion.matches ? 'Motion reduced' : (paused ? 'Play motion ▷' : 'Pause motion Ⅱ');
}
motionButton.addEventListener('click', () => { userPausedMotion = !userPausedMotion; updateMotion(); });
document.addEventListener('visibilitychange', updateMotion);
reducedMotion.addEventListener('change', updateMotion);
updateMotion();

const phases = [
  { name: 'Foundation', title: 'A stronger starting point.', description: 'We audit your customer journey, define your offer, and connect your tracking and tools. A considered foundation for everything that follows.', tags: ['Systems audit', 'Measurement', 'Offer alignment'] },
  { name: 'Awareness', title: 'A message worth noticing.', description: 'We clarify your positioning and bring your offer to the right audience. Every channel begins with a shared understanding of who you serve and why it matters.', tags: ['Brand positioning', 'Creative strategy', 'Audience research'] },
  { name: 'Acquisition', title: 'Attention with a next step.', description: 'We connect targeted campaigns to focused landing pages and a clear qualification journey. Your team sees the context behind each new inquiry.', tags: ['Paid campaigns', 'Landing pages', 'Lead qualification'] },
  { name: 'Nurturing', title: 'Keep the connection alive.', description: 'We design follow-up around your customer journey, with thoughtful messages and clear handoffs. Inquiries move toward a conversation instead of getting lost.', tags: ['Follow-up flows', 'Lead routing', 'Booking journey'] },
  { name: 'Scaling', title: 'Build on what you learn.', description: 'We review conversion data, find friction, and refine the system. Expansion follows evidence, with your team’s capacity and customer experience in view.', tags: ['Conversion review', 'Budget planning', 'Continuous improvement'] }
];
document.querySelectorAll('[data-phase]').forEach(button => {
  button.addEventListener('click', () => {
    const index = Number(button.dataset.phase);
    const phase = phases[index];
    document.querySelectorAll('[data-phase]').forEach(item => {
      const selected = item === button;
      item.classList.toggle('active', selected);
      item.setAttribute('aria-expanded', String(selected));
    });
    document.querySelector('.phase-art').dataset.step = String(index);
    document.querySelector('#phase-kicker').textContent = `Phase 0${index + 1} / ${phase.name}`;
    document.querySelector('#phase-title').textContent = phase.title;
    document.querySelector('#phase-description').textContent = phase.description;
    document.querySelector('#phase-tags').replaceChildren(...phase.tags.map(tag => {
      const span = document.createElement('span');
      span.textContent = tag;
      return span;
    }));
  });
});

const contactDialog = document.querySelector('#contact-dialog');
const legalDialog = document.querySelector('#legal-dialog');
const form = document.querySelector('#contact-form');
const status = document.querySelector('#form-status');
const submit = document.querySelector('#submit-contact');
let returnFocus = null;
function openDialog(dialog, trigger) {
  returnFocus = trigger;
  closeMenu();
  dialog.showModal();
}
document.querySelectorAll('[data-contact]').forEach(button => {
  button.addEventListener('click', () => openDialog(contactDialog, button));
});
document.querySelectorAll('dialog').forEach(dialog => {
  dialog.querySelector('[data-close]').addEventListener('click', () => dialog.close());
  dialog.addEventListener('click', event => {
    const rect = dialog.getBoundingClientRect();
    if (event.target === dialog && (event.clientX < rect.left || event.clientX > rect.right || event.clientY < rect.top || event.clientY > rect.bottom)) dialog.close();
  });
  dialog.addEventListener('close', () => { if (returnFocus) returnFocus.focus(); });
});
document.querySelectorAll('[data-legal]').forEach(button => {
  button.addEventListener('click', async () => {
    const type = button.dataset.legal;
    const body = document.querySelector('#legal-body');
    document.querySelector('#legal-title').textContent = type === 'privacy' ? 'Privacy policy' : 'Terms of service';
    body.textContent = 'Loading…';
    openDialog(legalDialog, button);
    try {
      const response = await fetch(`/assets/${type}.txt`);
      if (!response.ok) throw new Error('Legal content unavailable');
      body.textContent = await response.text();
    } catch {
      body.textContent = 'This document is temporarily unavailable. Please contact connect@veluseagency.com for a copy.';
    }
  });
});
form.addEventListener('submit', async event => {
  event.preventDefault();
  if (!form.reportValidity() || submit.disabled) return;
  const payload = Object.fromEntries(new FormData(form));
  Object.keys(payload).forEach(key => { payload[key] = payload[key].trim(); });
  if (Object.values(payload).some(value => !value)) {
    status.textContent = 'Please complete each field with your business details.';
    return;
  }
  submit.disabled = true;
  submit.textContent = 'Sending your request…';
  status.textContent = '';
  try {
    await fetch(intakeEndpoint, {
      method: 'POST', mode: 'no-cors',
      headers: { 'Content-Type': 'text/plain; charset=utf-8' },
      body: JSON.stringify(payload), signal: AbortSignal.timeout(15000)
    });
    // An opaque no-cors response cannot verify that the backend saved a lead.
    status.textContent = 'Your request was sent, but receipt cannot be confirmed here. If you don’t hear back, email connect@veluseagency.com.';
    submit.textContent = 'Request sent';
    form.reset();
  } catch {
    status.textContent = 'We couldn’t confirm delivery. Please try again or email connect@veluseagency.com.';
    submit.disabled = false;
    submit.textContent = 'Try again';
  }
});
document.querySelector('#year').textContent = new Date().getFullYear();
