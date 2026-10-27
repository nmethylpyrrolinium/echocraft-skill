const canvas = document.querySelector("canvas");
const ctx = canvas.getContext("2d");
function frame(t) { ctx.clearRect(0, 0, 300, 300); ctx.fillRect(t % 300, 10, 8, 8); requestAnimationFrame(frame); }
requestAnimationFrame(frame);
