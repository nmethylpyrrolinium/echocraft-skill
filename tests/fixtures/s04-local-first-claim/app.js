// Fixture: invented code. Syncs entries to a remote database while the page promises local-only.
const client = createClient("https://example-project.example.invalid", "PLACEHOLDER");
document.getElementById("save").addEventListener("click", async () => {
  const text = document.getElementById("entry").value;
  localStorage.setItem("tidewrite_entries", JSON.stringify([text]));
  await client.from("entries").insert({ body: text });
});
document.getElementById("wipe").addEventListener("click", () => {
  localStorage.removeItem("tidewrite_entries");
});
