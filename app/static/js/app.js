// Disable the extract button after click so a slow AI call can't be submitted twice.
document.addEventListener("submit", function (e) {
  const btn = e.target.querySelector("#extract-btn");
  if (btn) { btn.disabled = true; btn.textContent = "Extracting…"; }
});
