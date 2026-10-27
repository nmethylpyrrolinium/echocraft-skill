// Tidewrite (revised fixture): invented code for demonstration. Not a real product.
const client = createClient("https://example-project.example.invalid", "PLACEHOLDER");
const settings = { syncEnabled: false }; // opt-in; toggled from Settings (not shown in this fixture)
const canvas = document.querySelector(".tide-canvas");
const ctx = canvas.getContext("2d");
const reduce = window.matchMedia("(prefers-reduced-motion: reduce)");
let running = false;

function draw(t) { ctx.clearRect(0, 0, 800, 600); ctx.fillRect(t % 800, 300, 40, 4); }
function loop(t) { if (!running) return; draw(t); requestAnimationFrame(loop); }
function update() {
  const calm = reduce.matches || document.body.classList.contains("calm");
  running = !calm && !document.hidden;
  if (running) requestAnimationFrame(loop); else draw(0);
}
reduce.addEventListener("change", update);
document.addEventListener("visibilitychange", update);
document.getElementById("motion").addEventListener("change", (e) => {
  document.body.classList.toggle("calm", e.target.checked);
  update();
});
update();

function say(msg) { document.getElementById("toast").textContent = msg; }

document.getElementById("save").addEventListener("click", async () => {
  const body = document.getElementById("entry").value;
  localStorage.setItem("tidewrite_entries", JSON.stringify([body]));
  if (settings.syncEnabled) await client.from("entries").insert({ body });
  say("Saved on this device" + (settings.syncEnabled ? " and synced." : "."));
});

document.getElementById("wipe").addEventListener("click", async () => {
  if (!window.confirm("Remove your entries from this device?")) return;
  localStorage.removeItem("tidewrite_entries");
  if (settings.syncEnabled) await client.from("entries").delete().eq("owner", "current-user");
  say("Removed from this device." + (settings.syncEnabled ? " A remove request was sent to sync." : ""));
});
