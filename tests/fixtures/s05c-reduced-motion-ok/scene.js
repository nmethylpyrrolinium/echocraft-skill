const reduce = window.matchMedia("(prefers-reduced-motion: reduce)").matches;
const ctx = document.querySelector("canvas").getContext("2d");
function draw(t) { ctx.clearRect(0, 0, 300, 300); ctx.fillRect(t % 300, 10, 8, 8); }
if (reduce) { draw(0); } else { (function loop(t) { draw(t); requestAnimationFrame(loop); })(0); }
