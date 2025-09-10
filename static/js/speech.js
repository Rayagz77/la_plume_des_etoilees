// static/js/generator/speech.js

// ---------------- Speech-to-text (micro) ----------------
function createRecognizer(lang = "fr-FR") {
  const Rec = window.SpeechRecognition || window.webkitSpeechRecognition;
  if (!Rec) return null;
  const rec = new Rec();
  rec.lang = lang;
  rec.interimResults = false;
  rec.continuous = false;
  return rec;
}

document.addEventListener("click", (ev) => {
  const btn = ev.target.closest(".mic-btn");
  if (!btn) return;

  const inputId = btn.getAttribute("data-target");
  const input = document.getElementById(inputId);
  if (!input) {
    alert("Champ introuvable: " + inputId);
    return;
  }

  const rec = createRecognizer();
  if (!rec) {
    alert("Reconnaissance vocale non supportée par ce navigateur.");
    return;
  }

  btn.classList.add("listening"); // (ajoute un style si tu veux dans ton CSS)
  rec.start();

  rec.onresult = (e) => {
    const txt = (e.results?.[0]?.[0]?.transcript || "").trim();
    // on ajoute à la fin au lieu d’écraser
    input.value = (input.value ? input.value + " " : "") + txt;
    input.dispatchEvent(new Event("input", { bubbles: true }));
  };
  rec.onerror = () => btn.classList.remove("listening");
  rec.onend   = () => btn.classList.remove("listening");
});

// ---------------- Soumission du formulaire ----------------
const form = document.getElementById("story-form");
const container = document.getElementById("story-container");

function sanitize(s) {
  return String(s).replace(/</g, "&lt;").replace(/>/g, "&gt;");
}

form?.addEventListener("submit", async (e) => {
  e.preventDefault();
  container.textContent = "Génération en cours…";

  // Lis par ID (pas besoin d’attribut name)
  const payload = {
    age:       document.getElementById("age")?.value ?? 6,
    name:      document.getElementById("name")?.value ?? "",
    genre:     document.getElementById("genre")?.value ?? "",
    elements:  document.getElementById("elements")?.value ?? "",
    themes:    document.getElementById("themes")?.value ?? "",
    tone:      document.getElementById("tone")?.value ?? ""
  };

  try {
    const res  = await fetch("/story/api/generate", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(payload)
    });
    const data = await res.json();
    if (!res.ok || !data.story) throw new Error(data.error || "Erreur serveur");

    const safeStory = sanitize(data.story);
    container.innerHTML = ""; // nettoie

    // ----- Flipbook si dispo -----
    if (window.buildBook) {
      window.buildBook(safeStory);
    } else {
      // Essai d’import dynamique (au bon chemin)
      try {
        const mod = await import("/static/js/generator/flipbook.js");
        window.buildBook = mod.default || mod.buildBook;
        window.buildBook(safeStory);
      } catch (errImport) {
        console.warn("Flipbook indisponible, affichage brut.", errImport);
        container.innerHTML = `<pre style="white-space:pre-wrap;text-align:left;max-width:760px;margin:0 auto;">${safeStory}</pre>`;
      }
    }

    // ----- Liens de téléchargement / audio -----
    const extras = document.createElement("div");
    extras.className = "links";
    extras.innerHTML = `
      <p style="margin:12px 0;">
        <a href="${data.text_url}" download>⬇️ Télécharger le texte</a>
        ${data.audio_url ? ` • <a href="${data.audio_url}" download>🎧 Télécharger l'audio</a>` : ""}
      </p>
      ${data.audio_url ? `<audio controls style="width:100%;max-width:760px;"><source src="${data.audio_url}" type="audio/mpeg"></audio>` : ""}
    `;
    container.appendChild(extras);

  } catch (err) {
    console.error(err);
    container.innerHTML = `<p style="color:red;">${sanitize(err.message)}</p>`;
  }
});
