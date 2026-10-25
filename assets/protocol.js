'use strict';

// A native-scroll story. No wheel interception, synthetic scrolling, or click
// controls: the browser owns navigation and every chapter exists in the HTML.
(() => {
  const story = document.querySelector('[data-protocol-story]');
  if (!story) return;
  const stage = story.querySelector('.story-stage');
  const track = story.querySelector('.story-track');
  const chapters = [...story.querySelectorAll('[data-chapter]')];
  const scenes = [...story.querySelectorAll('[data-scene]')];
  const current = story.querySelector('.story-current');
  const count = story.querySelector('.story-count');
  const wide = window.matchMedia('(min-width: 900px)');
  const reduced = window.matchMedia('(prefers-reduced-motion: reduce)');
  const clamp = value => Math.max(0, Math.min(1, value));
  let frameId = 0;
  let activeIndex = -1;

  function render() {
    frameId = 0;
    const pinned = wide.matches && window.innerHeight >= 680 && !reduced.matches;
    story.classList.toggle('is-pinned', pinned);
    story.dataset.mode = pinned ? 'pinned' : 'flow';
    let index = 0;
    let local = 0;
    let overall = 0;

    if (pinned) {
      const rect = story.getBoundingClientRect();
      const distance = Math.max(1, rect.height - window.innerHeight);
      const progress = clamp(-rect.top / distance);
      const position = progress * (chapters.length - 1);
      const segment = Math.min(chapters.length - 1, Math.floor(position));
      const next = Math.min(segment + 1, chapters.length - 1);
      const offset = chapters[segment].offsetTop + (chapters[next].offsetTop - chapters[segment].offsetTop) * (position - segment);
      track.style.transform = `translate3d(0, ${-offset}px, 0)`;
      index = Math.min(chapters.length - 1, Math.round(position));
      const start = Math.max(0, index - 0.5);
      const end = Math.min(chapters.length - 1, index + 0.5);
      local = clamp((position - start) / Math.max(0.001, end - start));
      overall = (index + local) / chapters.length;
    } else {
      track.style.transform = '';
      const stageBottom = stage.getBoundingClientRect().bottom;
      const anchor = Math.min(window.innerHeight * 0.78, Math.max(window.innerHeight * 0.53, stageBottom + 40));
      const rects = chapters.map(chapter => chapter.getBoundingClientRect());
      rects.forEach((rect, i) => { if (rect.top <= anchor) index = i; });
      local = clamp((anchor - rects[index].top) / Math.max(1, rects[index].height));
      overall = (index + local) / chapters.length;
    }

    const quiet = reduced.matches || document.documentElement.classList.contains('motion-paused');
    stage.style.setProperty('--phase-progress', quiet ? '1' : local.toFixed(4));
    stage.style.setProperty('--draw', quiet ? '1' : clamp(0.08 + local * 1.55).toFixed(4));
    story.style.setProperty('--story-progress', clamp(overall).toFixed(4));
    story.dataset.active = String(index);
    document.documentElement.style.setProperty('--ambient-shift', quiet ? '0px' : `${(Math.sin(window.scrollY / 1800) * 35).toFixed(2)}px`);
    if (index !== activeIndex) {
      chapters.forEach((chapter, i) => chapter.classList.toggle('active', i === index));
      scenes.forEach((scene, i) => scene.classList.toggle('active', i === index));
      current.textContent = chapters[index].querySelector('.chapter-name').textContent;
      count.textContent = `${String(index + 1).padStart(2, '0')} / ${String(chapters.length).padStart(2, '0')}`;
      activeIndex = index;
    }
  }

  function schedule() {
    if (!frameId && !document.hidden) frameId = requestAnimationFrame(render);
  }
  window.addEventListener('scroll', schedule, { passive: true });
  window.addEventListener('resize', schedule, { passive: true });
  wide.addEventListener('change', schedule);
  reduced.addEventListener('change', schedule);
  new MutationObserver(schedule).observe(document.documentElement, { attributes: true, attributeFilter: ['class'] });
  document.addEventListener('visibilitychange', () => {
    if (document.hidden && frameId) { cancelAnimationFrame(frameId); frameId = 0; }
    else schedule();
  });
  schedule();
})();
