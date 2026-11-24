// A deterministic particle sculpture scrubbed by the five protocol chapters.
(() => {
  const canvas = document.querySelector('.phase-field');
  if (!canvas) return;
  const ctx = canvas.getContext('2d');
  if (!ctx) return;
  const story = canvas.closest('.protocol-story');
  const tau = 2 * Math.PI;
  let seed = 3219;
  function random() {
    seed = (Math.imul(seed, 1664525) + 1013904223) >>> 0;
    return seed / 4294967296;
  }
  const particles = Array.from({length: 2100}, (_, i) => ({
    a: random() * tau, r: Math.sqrt(random()), z: random() * 2 - 1,
    lane: i % 5, fleck: random(), tint: random()
  }));
  function position(p, phase) {
    const {a,r,z,lane}=p;
    const helix = r * 6.1 + lane * tau / 5 + z * (.16+.32*r);
    switch (phase) {
      case 0: { // A dense, tilted seed with a thin accretion disk.
        const radius = .18 + r*r*.45;
        return [Math.cos(a)*radius, Math.sin(a)*radius*.36+z*.04];
      }
      case 1: { // A shock front breaking into radial filaments.
        const ray = Math.round(a*13)/13 + z*.018;
        const radius = .12+r*(.76+.14*Math.cos(ray*5));
        return [Math.cos(ray)*radius, Math.sin(ray)*radius*.82];
      }
      case 2: { // Five streams converge at one aperture.
        const x = r*1.8-.9;
        return [x, Math.sin(x*3+lane*.36)*.18+(lane-2)*(.08+.19*x*x)+z*.045];
      }
      case 3: { // Two ribbons exchange strands.
        const h=r*8.5+lane*1.25;
        return [(r-.5)*1.65, Math.sin(h)*(.24+.08*Math.cos(r*4))+z*.035];
      }
      default: // An open, five-armed spiral.
        return [Math.cos(helix)*r,Math.sin(helix)*r*.59+z*.055*(1-r)];
    }
  }
  let frame = 0, visible = false;
  function render() {
    frame=0;
    const {width,height}=canvas.getBoundingClientRect();
    if (!width || !height) return;
    canvas.parentElement.classList.add('field-ready');
    const ratio=Math.min(window.devicePixelRatio||1,2);
    const w=Math.round(width*ratio), h=Math.round(height*ratio);
    if(canvas.width!==w || canvas.height!==h){canvas.width=w;canvas.height=h;}
    const quiet=document.documentElement.classList.contains('motion-paused');
    const progress=Number(story.style.getPropertyValue('--story-progress'))||0;
    const phase=quiet ? Number(story.dataset.active)||0 : Math.min(4,Math.max(0,progress*5-.5));
    const index=Math.floor(phase), next=Math.min(4,index+1);
    const t=phase-index, blend=t*t*(3-2*t);
    const turn=quiet ? -.25 : -.37+progress*.46;
    const c=Math.cos(turn), s=Math.sin(turn), scale=Math.min(width*.49,height*.51);
    ctx.setTransform(ratio,0,0,ratio,0,0);
    ctx.clearRect(0,0,width,height);
    ctx.translate(width/2,height/2);
    const mist=ctx.createRadialGradient(0,0,0,0,0,scale);
    mist.addColorStop(0,'#ffe3a6');mist.addColorStop(.025,'#dda561');mist.addColorStop(.09,'rgba(207,139,66,.54)');
    mist.addColorStop(.29,'rgba(109,100,60,.16)');mist.addColorStop(.64,'rgba(65,123,98,.065)');mist.addColorStop(1,'transparent');
    ctx.fillStyle=mist;ctx.fillRect(-width/2,-height/2,width,height);
    if(phase>3) {
      // Filaments gather into spiral arms as the final chapter comes into view.
      ctx.save();
      ctx.rotate(turn);ctx.scale(scale,scale*.59);
      ctx.lineWidth=1/scale;
      for(let arm=0;arm<5;arm++){
        for(let strand=-3;strand<=3;strand++){
          ctx.strokeStyle='rgba(136,197,158,'+((phase-3)*.13)+')';
          ctx.beginPath();
          for(let i=0;i<=64;i++){
            const r=i/64, a=r*6.1+arm*tau/5+strand*.05*Math.sin(r*4);
            const x=r*Math.cos(a),y=r*Math.sin(a);
            if(i===0)ctx.moveTo(x,y);else ctx.lineTo(x,y);
          }
          ctx.stroke();
        }
      }
      ctx.restore();
    }
    for (const p of particles) {
      const start=position(p,index), end=position(p,next);
      const u=start[0]+(end[0]-start[0])*blend, v=start[1]+(end[1]-start[1])*blend;
      const x=(c*u-s*v)*scale, y=(s*u+c*v)*scale;
      const size=(p.fleck>.97?2.4:.75+p.fleck*.9)*Math.max(.85,scale/240);
      ctx.globalAlpha=.43+p.fleck*.57;
      ctx.fillStyle=p.tint>.78?'#f5d39b':p.tint>.53?'#d3a253':p.tint>.16?'#7fb99b':'#dde4d8';
      ctx.fillRect(x,y,size,size);
      if(index===1 && p.fleck>.75){
        ctx.beginPath();ctx.moveTo(x*.94,y*.94);ctx.lineTo(x,y);ctx.strokeStyle=ctx.fillStyle;ctx.lineWidth=.55;ctx.stroke();
      }
    }
    ctx.globalAlpha=1;
  }
  function schedule(){if(visible && !document.hidden && !frame)frame=requestAnimationFrame(render);}
  new IntersectionObserver(([entry])=>{visible=entry.isIntersecting;schedule()}).observe(canvas);
  new ResizeObserver(schedule).observe(canvas);
  new MutationObserver(schedule).observe(story,{attributes:true,attributeFilter:['style','data-active']});
  new MutationObserver(schedule).observe(document.documentElement,{attributes:true,attributeFilter:['class']});
  document.addEventListener('visibilitychange',schedule);
})();
