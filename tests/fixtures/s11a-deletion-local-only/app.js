const client = createClient("https://example-project.example.invalid", "PLACEHOLDER");
async function save(text) { await client.from("entries").insert({ body: text }); localStorage.setItem("diary_cache", text); }
function deleteEverything() { localStorage.clear(); alert("Everything deleted."); }
