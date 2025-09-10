# controllers/generateur_controller.py
from flask import Blueprint, request, jsonify, render_template, url_for, current_app
from services.story_service import generate_and_save

bp = Blueprint("story", __name__, url_prefix="/story")

@bp.get("/generator")
def page_generator():
    return render_template("generator/generateur.html")

@bp.post("/api/generate")
def api_generate():
    data = request.get_json(force=True) or {}
    try:
        result = generate_and_save(data, current_app.logger)
        text_url = url_for("static", filename=f"stories/{result['text_filename']}")
        audio_url = (
            url_for("static", filename=f"stories/{result['audio_filename']}")
            if result.get("audio_filename") else None
        )
        return jsonify(story=result["story"], text_url=text_url, audio_url=audio_url)
    except Exception as e:
        current_app.logger.exception("Erreur génération")
        return jsonify(error=str(e)), 500
