"""
BioSense360 — API REST Flask
==============================
Expose le modèle Random Forest via une API REST légère.
Utilise le pattern Application Factory pour faciliter les tests unitaires.

Endpoints :
    GET  /health   → Santé du service + informations modèle
    POST /predict  → Prédiction depuis {temperature, humidite}
    GET  /seuils   → Tableau complet des seuils critiques

Usage :
    # Démarrage direct
    python -m biosense360.api

    # Ou depuis un script
    from biosense360.api import create_app
    app = create_app()
    app.run(host="0.0.0.0", port=5000)
"""

from __future__ import annotations

import logging
import os

from flask import Flask, jsonify, request

from ..config import API_DEBUG, API_HOST, API_PORT, DEFAULT_MODEL_PATH, SYSTEME_ALARME
from ..predictor import BioSensePredictor

logger = logging.getLogger(__name__)


def create_app(model_path: str | None = None) -> Flask:
    """Crée et configure l'application Flask (Application Factory).

    Parameters
    ----------
    model_path : str | None
        Chemin vers le fichier .pkl du modèle. Si None, utilise
        DEFAULT_MODEL_PATH (configurable via BIOSENSE_MODEL_PATH).

    Returns
    -------
    Flask
        Application Flask configurée avec tous les endpoints.

    Examples
    --------
    >>> app = create_app("models/modele_rf.pkl")
    >>> client = app.test_client()
    >>> resp = client.get("/health")
    >>> assert resp.status_code == 200
    """
    app = Flask(__name__)

    # ------------------------------------------------------------------
    # Chargement du modèle (une seule fois au démarrage)
    # ------------------------------------------------------------------
    resolved_path = model_path or DEFAULT_MODEL_PATH
    predictor = BioSensePredictor.from_file(resolved_path)
    app.config["PREDICTOR"] = predictor

    # ------------------------------------------------------------------
    # Enregistrement des routes
    # ------------------------------------------------------------------
    _register_routes(app)

    logger.info(
        "Application BioSense360 créée — modèle : %s", resolved_path
    )
    return app


def _register_routes(app: Flask) -> None:
    """Enregistre tous les endpoints sur l'application Flask."""

    # ---------------------------------------------------------------
    # GET /health
    # ---------------------------------------------------------------
    @app.route("/health", methods=["GET"])
    def health():
        """Vérification de santé du service.

        Returns
        -------
        JSON
            ``{"status": "ok", "modele": {...}}``
        """
        predictor: BioSensePredictor = app.config["PREDICTOR"]
        return jsonify({
            "status": "ok",
            "service": "BioSense360 API",
            "version": "1.0.0",
            "modele": predictor.model_info,
        }), 200

    # ---------------------------------------------------------------
    # POST /predict
    # ---------------------------------------------------------------
    @app.route("/predict", methods=["POST"])
    def predict():
        """Prédit la vivabilité thermique à partir des données capteur.

        Body JSON attendu :
            ``{"temperature": 35.0, "humidite": 70}``

        Returns
        -------
        JSON
            Rapport complet de prédiction (classe, Humidex, niveau, protocole).

        Exemples d'appel :
            .. code-block:: bash

                curl -X POST http://localhost:5000/predict \\
                  -H "Content-Type: application/json" \\
                  -d '{"temperature": 35.0, "humidite": 70}'
        """
        predictor: BioSensePredictor = app.config["PREDICTOR"]
        data = request.get_json(silent=True)

        # Validation du corps de la requête
        if not data:
            return jsonify({"erreur": "Corps JSON manquant ou malformé."}), 400

        missing = [f for f in ("temperature", "humidite") if f not in data]
        if missing:
            return jsonify({
                "erreur": f"Champ(s) requis manquant(s) : {', '.join(missing)}"
            }), 400

        try:
            temperature = float(data["temperature"])
            humidite = float(data["humidite"])
        except (ValueError, TypeError):
            return jsonify({
                "erreur": "Les champs 'temperature' et 'humidite' doivent être numériques."
            }), 400

        try:
            result = predictor.predict(temperature=temperature, humidite=humidite)
        except ValueError as exc:
            return jsonify({"erreur": str(exc)}), 422

        return jsonify(result.to_dict()), 200

    # ---------------------------------------------------------------
    # GET /seuils
    # ---------------------------------------------------------------
    @app.route("/seuils", methods=["GET"])
    def seuils():
        """Retourne le tableau complet des seuils critiques Humidex.

        Returns
        -------
        JSON
            Dictionnaire ``{classe: {seuil, niveau, conseil, protocole}}``.
        """
        return jsonify({
            str(classe): {
                "seuil": info.seuil,
                "niveau": info.niveau,
                "conseil": info.conseil,
                "protocole": list(info.protocole),
            }
            for classe, info in SYSTEME_ALARME.items()
        }), 200


# ---------------------------------------------------------------------------
# Point d'entrée direct
# ---------------------------------------------------------------------------

if __name__ == "__main__":
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s [%(levelname)s] %(name)s — %(message)s",
    )

    print()
    print("  ╔══════════════════════════════════════════════════╗")
    print("  ║      BioSense360 — API de Vivabilité Active      ║")
    print("  ╠══════════════════════════════════════════════════╣")
    print("  ║  GET  /health   → État du service + modèle       ║")
    print("  ║  POST /predict  → Prédiction temps réel          ║")
    print("  ║  GET  /seuils   → Seuils critiques Humidex       ║")
    print("  ╚══════════════════════════════════════════════════╝")
    print()

    app = create_app()
    app.run(host=API_HOST, port=API_PORT, debug=API_DEBUG)
