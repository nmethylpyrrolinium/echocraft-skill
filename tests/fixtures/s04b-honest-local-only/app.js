document.getElementById("save").addEventListener("click", () => {
  localStorage.setItem("tidewrite_entries", JSON.stringify([document.getElementById("entry").value]));
});
document.getElementById("wipe").addEventListener("click", () => localStorage.removeItem("tidewrite_entries"));
