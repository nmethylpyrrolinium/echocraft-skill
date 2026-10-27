const client = createClient("https://example-project.example.invalid", "PLACEHOLDER");
async function save(text) { await client.from("entries").insert({ body: text }); }
