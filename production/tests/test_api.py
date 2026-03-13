"""
Tests unitaires — API REST Flask
===================================
Valide les trois endpoints : /health, /predict, /seuils.
Utilise le client Flask de test (pas de serveur requis).
"""

from __future__ import annotations

import json

import pytest


class TestHealthEndpoint:
    """Tests de GET /health."""

    def test_retourne_200(self, flask_client):
        resp = flask_client.get("/health")
        assert resp.status_code == 200

    def test_status_ok(self, flask_client):
        data = json.loads(flask_client.get("/health").data)
        assert data["status"] == "ok"

    def test_champs_modele_presents(self, flask_client):
        data = json.loads(flask_client.get("/health").data)
        assert "modele" in data
        assert "n_estimators" in data["modele"]


class TestPredictEndpoint:
    """Tests de POST /predict."""

    def _post(self, flask_client, payload):
        return flask_client.post(
            "/predict",
            data=json.dumps(payload),
            content_type="application/json",
        )

    # --- Cas nominaux ---

    def test_retourne_200_avec_entrees_valides(self, flask_client):
        resp = self._post(flask_client, {"temperature": 22.0, "humidite": 55.0})
        assert resp.status_code == 200

    def test_structure_reponse(self, flask_client):
        data = json.loads(
            self._post(flask_client, {"temperature": 22.0, "humidite": 55.0}).data
        )
        for champ in ("timestamp", "entree", "humidex", "classe", "niveau", "conseil", "protocole"):
            assert champ in data, f"Champ manquant dans la réponse : {champ}"

    def test_humidex_est_float(self, flask_client):
        data = json.loads(
            self._post(flask_client, {"temperature": 30.0, "humidite": 60.0}).data
        )
        assert isinstance(data["humidex"], float)

    def test_classe_dans_plage(self, flask_client):
        data = json.loads(
            self._post(flask_client, {"temperature": 35.0, "humidite": 70.0}).data
        )
        assert 0 <= data["classe"] <= 7

    def test_entree_reflectee(self, flask_client):
        payload = {"temperature": 28.5, "humidite": 62.0}
        data = json.loads(self._post(flask_client, payload).data)
        assert data["entree"]["temperature"] == 28.5
        assert data["entree"]["humidite"] == 62.0

    # --- Cas d'erreur ---

    def test_corps_vide_retourne_400(self, flask_client):
        resp = flask_client.post("/predict", data="", content_type="application/json")
        assert resp.status_code == 400

    def test_champ_temperature_manquant_retourne_400(self, flask_client):
        resp = self._post(flask_client, {"humidite": 50.0})
        assert resp.status_code == 400

    def test_champ_humidite_manquant_retourne_400(self, flask_client):
        resp = self._post(flask_client, {"temperature": 25.0})
        assert resp.status_code == 400

    def test_type_invalide_retourne_400(self, flask_client):
        resp = self._post(flask_client, {"temperature": "chaud", "humidite": 50.0})
        assert resp.status_code == 400

    def test_temperature_hors_plage_retourne_422(self, flask_client):
        resp = self._post(flask_client, {"temperature": 100.0, "humidite": 50.0})
        assert resp.status_code == 422

    def test_humidite_hors_plage_retourne_422(self, flask_client):
        resp = self._post(flask_client, {"temperature": 25.0, "humidite": 200.0})
        assert resp.status_code == 422


class TestSeuilsEndpoint:
    """Tests de GET /seuils."""

    def test_retourne_200(self, flask_client):
        resp = flask_client.get("/seuils")
        assert resp.status_code == 200

    def test_huit_classes(self, flask_client):
        data = json.loads(flask_client.get("/seuils").data)
        assert len(data) == 8

    def test_toutes_les_classes_presentes(self, flask_client):
        data = json.loads(flask_client.get("/seuils").data)
        for i in range(8):
            assert str(i) in data, f"Classe {i} manquante dans /seuils"

    def test_structure_classe(self, flask_client):
        data = json.loads(flask_client.get("/seuils").data)
        for classe, info in data.items():
            assert "seuil" in info
            assert "niveau" in info
            assert "conseil" in info
            assert "protocole" in info
            assert isinstance(info["protocole"], list)
