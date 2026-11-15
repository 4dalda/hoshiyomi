'use strict';
// Set the verified application URL here when supplied. No data is collected locally.
const CONSULT_URL = '';
const motion = window.matchMedia('(prefers-reduced-motion: reduce)');
const mobile = window.matchMedia('(max-width: 700px)');
const hero = document.querySelector('.hero');
const scene = document.querySelector('.scene');
const layers = Object.fromEntries([...document.querySelectorAll('[data-layer]')].map(el => [el.dataset.layer, el]));
let frame = 0;
let start = 0;
let travel = 1;
let height = 0;
function measure() {
  start = hero.getBoundingClientRect().top + window.scrollY;
  height = scene.offsetHeight;
  travel = Math.max(1, hero.offsetHeight - height);
}
function render() {
  frame = 0;
  const progress = motion.matches ? 0 : Math.max(0, Math.min(1, (window.scrollY - start) / travel));
  const scale = mobile.matches ? 0.52 : 1;
  // Foreground crosses the scene faster; the cafe remains visible behind it.
  layers.background.style.transform = `translate3d(0,${-progress * height * 0.09 * scale}px,0) scale(${1.02 + progress * 0.035})`;
  layers.light.style.transform = `translate3d(${-progress * 35 * scale}px,${-progress * height * 0.19 * scale}px,0)`;
  layers.person.style.transform = `translate3d(${progress * 35 * scale}px,${-progress * height * 0.43 * scale}px,0)`;
  layers.text.style.transform = `translate3d(0,${-progress * height * 0.63 * scale}px,0)`;
}
function schedule() { if (!frame) frame = requestAnimationFrame(render); }
function resize() { measure(); schedule(); }
window.addEventListener('scroll', schedule, {passive:true});
window.addEventListener('resize', resize, {passive:true});
window.addEventListener('pageshow', resize);
motion.addEventListener('change', resize);
mobile.addEventListener('change', resize);
measure(); render();
// Only enable hidden reveal states after the observer exists. Content survives JS failure.
if ('IntersectionObserver' in window && !motion.matches) {
  const observer = new IntersectionObserver(entries => {
    for (const entry of entries) if (entry.isIntersecting) {
      entry.target.classList.add('visible'); observer.unobserve(entry.target);
    }
  }, {threshold:0.12});
  document.documentElement.classList.add('motion');
  document.querySelectorAll('.reveal').forEach(el => observer.observe(el));
}
const dialog = document.getElementById('consult-dialog');
for (const button of document.querySelectorAll('[data-consult]')) button.addEventListener('click', () => {
  if (CONSULT_URL) window.location.assign(CONSULT_URL);
  else dialog.showModal();
});
for (const button of dialog.querySelectorAll('button')) button.addEventListener('click', () => dialog.close());
dialog.addEventListener('click', event => { if (event.target === dialog) {
  const rect = dialog.getBoundingClientRect();
  if (event.clientX < rect.left || event.clientX > rect.right || event.clientY < rect.top || event.clientY > rect.bottom) dialog.close();
}});
