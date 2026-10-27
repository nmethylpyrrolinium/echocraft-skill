// Tidewrite fixture: invented code for demonstration. Not a real product.
const client = createClient("https://example-project.example.invalid", "PLACEHOLDER");
const ctx = document.querySelector(".tide-canvas").getContext("2d");
function waves(t) { ctx.clearRect(0, 0, 800, 600); ctx.fillRect(t % 800, 300, 40, 4); requestAnimationFrame(waves); }
requestAnimationFrame(waves);

document.getElementById("save").addEventListener("click", async () => {
  const body = document.getElementById("entry").value;
  localStorage.setItem("tidewrite_entries", JSON.stringify([body]));
  await client.from("entries").insert({ body });
  const t = document.getElementById("toast");
  t.textContent = "Saved."; t.classList.add("on");
  confetti();
});

document.getElementById("wipe").addEventListener("click", () => {
  localStorage.removeItem("tidewrite_entries");
  alert("Everything deleted.");
});
