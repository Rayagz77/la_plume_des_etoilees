# services/story_service.py
from __future__ import annotations
import os
import re
from pathlib import Path
from datetime import datetime

BASE_DIR = Path(__file__).resolve().parents[1]
STORIES_DIR = BASE_DIR / "static" / "stories"
STORIES_DIR.mkdir(parents=True, exist_ok=True)

SAFE_NAME_RE = re.compile(r"[^a-zA-Z0-9_\-]+")

def _slug(s: str) -> str:
    s = s.strip().lower().replace(" ", "_")
    return SAFE_NAME_RE.sub("", s)

def generate_and_save(data: dict, logger) -> dict:
    """
    Génère une histoire 'placeholder', la sauvegarde en .txt dans static/stories
    et retourne {story, text_filename, audio_filename}.
    """
    age = str(data.get("age", "")).strip() or "6"
    name = str(data.get("name", "")).strip() or "Axelle"
    genre = str(data.get("genre", "")).strip() or "Conte animalier"
    elements = str(data.get("elements", "")).strip() or "animaux qui parlent, rimes, comptine"
    themes = str(data.get("themes", "")).strip() or "confiance en soi"
    tone = str(data.get("tone", "")).strip() or "joyeux et rassurant"

    # --- Histoire simple (pas d’IA) ---
    story = f"""Titre : Le voyage de {name}

Pour un enfant de {age} ans — {genre}

Dans une clairière au cœur de la forêt, {name} rêvait d’aventure.
Guidé(e) par un refrain enjoué, {name} rencontrait des amis extraordinaires :
un renard rieur, une chouette qui aimait compter en rimes,
et un hérisson timide qui battait la mesure de ses petits pas.

Avec des {elements}, l’histoire prenait des couleurs et des sons.
Quand {name} doutait, la forêt murmura : “Tu peux le faire !”
Petit à petit, grâce à l’{themes}, {name} retrouva le sourire.

Au crépuscule, un dernier refrain emplit l’air,
dans un ton {tone}, et l’aventure se referma comme un livre :
{ name } sut que la confiance pousse comme une fleur
dès qu’on arrose ses rêves d’un peu de courage.
"""

    # --- Sauvegarde .txt ---
    ts = datetime.now().strftime("%Y%m%d_%H%M%S")
    base = f"{ts}_{_slug(name) or 'histoire'}"
    text_filename = f"{base}.txt"
    (STORIES_DIR / text_filename).write_text(story, encoding="utf-8")

    # Pas d’audio par défaut (tu pourras l’ajouter plus tard)
    audio_filename = None

    logger.info(f"Story saved → static/stories/{text_filename}")
    return dict(story=story, text_filename=text_filename, audio_filename=audio_filename)
