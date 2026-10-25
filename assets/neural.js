'use strict';

// The original Veluse motif: drifting nodes, proximity connections, repulsion,
// and signals firing between neighbors. No coordinates are stored or sent.
(() => {
  const canvas = document.querySelector('#telemetryCanvas');
  if (!canvas) return;
  const context = canvas.getContext('2d', { alpha: true });
  if (!context) return;
  const preference = window.matchMedia('(prefers-reduced-motion: reduce)');
  let width = 0;
  let height = 0;
  let nodes = [];
  let pulses = [];
  let frameId = 0;
  let lastFrame = 0;
  let emissionTime = 0;
  let connectionDistance = 220;
  const pointer = { x: null, y: null, targetX: null, targetY: null, radius: 200 };

  function resize() {
    const oldWidth = width;
    const oldHeight = height;
    width = window.innerWidth;
    height = window.innerHeight;
    const mobile = width < 768;
    const count = mobile ? 42 : 140;
    connectionDistance = mobile ? 135 : Math.min(240, width * 0.19);
    const ratio = Math.min(window.devicePixelRatio || 1, 2);
    canvas.width = Math.round(width * ratio);
    canvas.height = Math.round(height * ratio);
    context.setTransform(ratio, 0, 0, ratio, 0, 0);
    if (nodes.length !== count) {
      nodes = Array.from({ length: count }, () => {
        const vx = (Math.random() - 0.5) * (mobile ? 0.42 : 0.68);
        const vy = (Math.random() - 0.5) * (mobile ? 0.42 : 0.68);
        return { x: Math.random() * width, y: Math.random() * height, vx, vy, baseVx: vx, baseVy: vy, charge: 0 };
      });
      pulses = [];
    } else if (oldWidth && oldHeight) {
      nodes.forEach(node => { node.x *= width / oldWidth; node.y *= height / oldHeight; });
    }
    draw(0, false);
  }

  function neighbors(node, exclude) {
    return nodes.filter(other => other !== node && other !== exclude && Math.hypot(other.x - node.x, other.y - node.y) < connectionDistance);
  }

  function fire(from, previous, hops = 0) {
    if (pulses.length >= 42) return;
    const options = neighbors(from, previous);
    if (!options.length) return;
    const to = options[Math.floor(Math.random() * options.length)];
    from.charge = 1;
    pulses.push({ from, to, progress: 0, speed: 0.012 + Math.random() * 0.014, cyan: Math.random() < 0.32, hops });
  }

  function draw(delta, animate) {
    context.clearRect(0, 0, width, height);
    if (animate) {
      if (pointer.targetX !== null) {
        if (pointer.x === null) { pointer.x = pointer.targetX; pointer.y = pointer.targetY; }
        pointer.x += (pointer.targetX - pointer.x) * 0.1 * delta;
        pointer.y += (pointer.targetY - pointer.y) * 0.1 * delta;
      }
      nodes.forEach(node => {
        if (pointer.x !== null) {
          const dx = node.x - pointer.x;
          const dy = node.y - pointer.y;
          const distance = Math.hypot(dx, dy);
          if (distance > 0 && distance < pointer.radius) {
            const force = (1 - distance / pointer.radius) * 0.2;
            node.vx += (dx / distance) * force * delta;
            node.vy += (dy / distance) * force * delta;
          }
        }
        node.vx += (node.baseVx - node.vx) * 0.035 * delta;
        node.vy += (node.baseVy - node.vy) * 0.035 * delta;
        node.x += node.vx * delta;
        node.y += node.vy * delta;
        if (node.x < -25) node.x = width + 25;
        if (node.x > width + 25) node.x = -25;
        if (node.y < -25) node.y = height + 25;
        if (node.y > height + 25) node.y = -25;
        node.charge = Math.max(0, node.charge - 0.025 * delta);
      });
    }

    context.lineWidth = 0.7;
    for (let i = 0; i < nodes.length; i++) {
      for (let j = i + 1; j < nodes.length; j++) {
        const a = nodes[i];
        const b = nodes[j];
        const distance = Math.hypot(a.x - b.x, a.y - b.y);
        if (distance >= connectionDistance) continue;
        const alpha = (1 - distance / connectionDistance) * 0.42;
        context.strokeStyle = `rgba(91, 77, 231, ${alpha})`;
        context.beginPath();
        context.moveTo(a.x, a.y);
        context.lineTo(b.x, b.y);
        context.stroke();
      }
    }
    nodes.forEach(node => {
      context.fillStyle = node.charge > 0.3 ? `rgba(30, 199, 239, ${0.5 + node.charge * 0.5})` : 'rgba(112, 95, 244, 0.65)';
      const size = node.charge > 0.3 ? 3.2 : 2.1;
      context.fillRect(node.x - size / 2, node.y - size / 2, size, size);
    });

    if (animate) {
      emissionTime += delta * 16.667;
      if (emissionTime >= 95) {
        fire(nodes[Math.floor(Math.random() * nodes.length)]);
        emissionTime = 0;
      }
      for (let i = pulses.length - 1; i >= 0; i--) {
        const pulse = pulses[i];
        pulse.progress += pulse.speed * delta;
        if (pulse.progress >= 1) {
          pulse.to.charge = 1;
          pulses.splice(i, 1);
          if (pulse.hops < 2 && Math.random() < 0.45) fire(pulse.to, pulse.from, pulse.hops + 1);
          continue;
        }
        if (Math.hypot(pulse.to.x - pulse.from.x, pulse.to.y - pulse.from.y) > connectionDistance * 1.8) {
          pulses.splice(i, 1);
          continue;
        }
        const progress = pulse.progress;
        const tail = Math.max(0, progress - 0.28);
        const x = pulse.from.x + (pulse.to.x - pulse.from.x) * progress;
        const y = pulse.from.y + (pulse.to.y - pulse.from.y) * progress;
        const color = pulse.cyan ? '#06c9e8' : '#8473ff';
        context.lineWidth = 1.2;
        context.strokeStyle = color;
        context.beginPath();
        context.moveTo(pulse.from.x + (pulse.to.x - pulse.from.x) * tail, pulse.from.y + (pulse.to.y - pulse.from.y) * tail);
        context.lineTo(x, y);
        context.stroke();
        context.shadowBlur = 9;
        context.shadowColor = color;
        context.fillStyle = color;
        context.beginPath();
        context.arc(x, y, 2, 0, Math.PI * 2);
        context.fill();
        context.shadowBlur = 0;
      }
    }
  }

  function paused() {
    return document.hidden || preference.matches || document.documentElement.classList.contains('motion-paused');
  }
  function frame(now) {
    frameId = 0;
    if (paused()) return;
    const delta = lastFrame ? Math.min((now - lastFrame) / 16.667, 2) : 1;
    lastFrame = now;
    draw(delta, true);
    frameId = requestAnimationFrame(frame);
  }
  function syncMotion() {
    if (paused()) {
      if (frameId) cancelAnimationFrame(frameId);
      frameId = 0;
      lastFrame = 0;
      if (preference.matches) draw(0, false);
    } else if (!frameId) {
      lastFrame = 0;
      frameId = requestAnimationFrame(frame);
    }
  }
  window.addEventListener('pointermove', event => {
    if (event.pointerType === 'touch') return;
    pointer.targetX = event.clientX;
    pointer.targetY = event.clientY;
  }, { passive: true });
  document.addEventListener('pointerleave', () => {
    pointer.x = pointer.y = pointer.targetX = pointer.targetY = null;
  });
  window.addEventListener('resize', resize, { passive: true });
  document.addEventListener('visibilitychange', syncMotion);
  preference.addEventListener('change', syncMotion);
  new MutationObserver(syncMotion).observe(document.documentElement, { attributes: true, attributeFilter: ['class'] });
  resize();
  syncMotion();
})();
