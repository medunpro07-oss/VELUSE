(() => {
  const area=document.querySelector('.opening');
  const art=area.querySelector('.opening-art');
  const fine=window.matchMedia('(hover:hover) and (pointer:fine)');
  const reduced=window.matchMedia('(prefers-reduced-motion:reduce)');
  let frame=0, x=0, y=0;
  function paint(){
    frame=0;
    art.style.setProperty('--tilt-x',(y*-8).toFixed(2)+'deg');
    art.style.setProperty('--tilt-y',(x*12).toFixed(2)+'deg');
    art.style.setProperty('--drift-x',(x*12).toFixed(2)+'px');
    art.style.setProperty('--drift-y',(y*7).toFixed(2)+'px');
  }
  function reset(){if(frame)cancelAnimationFrame(frame);x=y=0;paint();}
  area.addEventListener('pointermove',event=>{
    if(!fine.matches || reduced.matches || document.hidden || document.documentElement.classList.contains('motion-paused'))return;
    const box=area.getBoundingClientRect();
    x=Math.max(-1,Math.min(1,(event.clientX-box.left)/box.width*2-1));
    y=Math.max(-1,Math.min(1,(event.clientY-box.top)/box.height*2-1));
    if(!frame)frame=requestAnimationFrame(paint);
  },{passive:true});
  area.addEventListener('pointerleave',reset);
  document.addEventListener('visibilitychange',reset);
  fine.addEventListener('change',reset);
  reduced.addEventListener('change',reset);
  new MutationObserver(reset).observe(document.documentElement,{attributes:true,attributeFilter:['class']});
})();
