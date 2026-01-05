// gestione filtri: multi‑selezione, stato iniziale "tutto attivo"
// logica: un bullet point resta visibile se ha almeno un tag attivo.[web:4][web:8]

document.addEventListener("DOMContentLoaded", () => {
  const buttons = Array.from(document.querySelectorAll(".filter-button"));
  const items   = Array.from(document.querySelectorAll(".bullets li"));

  // set iniziale: tutti i tag attivi
  const activeTags = new Set(
    buttons.map(btn => btn.dataset.tag)
  );

  buttons.forEach(button => {
    button.addEventListener("click", () => {
      const tag = button.dataset.tag;

      if (activeTags.has(tag)) {
        // spegni filtro
        activeTags.delete(tag);
        button.classList.remove("is-on");
        button.classList.add("is-off");
        button.setAttribute("aria-pressed", "false");
        button.querySelector(".filter-symbol").textContent = "+";
      } else {
        // riaccendi filtro
        activeTags.add(tag);
        button.classList.remove("is-off");
        button.classList.add("is-on");
        button.setAttribute("aria-pressed", "true");
        button.querySelector(".filter-symbol").textContent = "×";
      }

      applyFilters(items, activeTags);
    });
  });

  // applica i filtri ad ogni click
  applyFilters(items, activeTags);
});

function applyFilters(items, activeTags) {
  items.forEach(item => {
    const tags = (item.dataset.tags || "")
      .split(/\s+/)
      .filter(Boolean);

    // se non ci sono tag, mostralo sempre
    if (tags.length === 0) {
      item.classList.remove("is-hidden");
      return;
    }

    // visibile se almeno un tag è attivo
    const hasActive = tags.some(tag => activeTags.has(tag));

    if (hasActive) {
      item.classList.remove("is-hidden");
    } else {
      item.classList.add("is-hidden");
    }
  });
}
