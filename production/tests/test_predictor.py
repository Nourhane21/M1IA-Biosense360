"""
Tests unitaires — Module predictor
=====================================
Valide le comportement du BioSensePredictor : prédiction, validation
des entrées, structure du résultat et gestion des erreurs.
"""

from __future__ import annotations

from pathlib import Path
from unittest.mock import patch

import pytest

from biosense360.predictor import BioSensePredictor, PredictionResult


class TestBioSensePredictorPredict:
    """Tests de la méthode predict()."""

    def test_retourne_prediction_result(self, predictor):
        """predict() doit retourner un objet PredictionResult."""
        result = predictor.predict(temperature=20.0, humidite=50.0)
        assert isinstance(result, PredictionResult)

    def test_classe_valide(self, predictor):
        """La classe prédite doit être dans [0, 7]."""
        result = predictor.predict(temperature=35.0, humidite=60.0)
        assert 0 <= result.classe <= 7

    def test_humidex_coherent(self, predictor):
        """L'Humidex retourné doit être cohérent avec T et HR."""
        result = predictor.predict(temperature=30.0, humidite=60.0)
        # À 30°C / 60% HR, l'Humidex doit être > 30
        assert result.humidex > 30.0

    def test_champs_presents(self, predictor):
        """Tous les champs du PredictionResult doivent être remplis."""
        result = predictor.predict(temperature=25.0, humidite=55.0)
        assert result.timestamp
        assert result.temperature == 25.0
        assert result.humidite == 55.0
        assert isinstance(result.humidex, float)
        assert isinstance(result.classe, int)
        assert result.seuil
        assert result.niveau
        assert result.conseil
        assert isinstance(result.protocole, list)
        assert len(result.protocole) >= 1

    def test_to_dict_json_compatible(self, predictor):
        """to_dict() doit retourner un dictionnaire JSON-compatible."""
        import json

        result = predictor.predict(temperature=20.0, humidite=50.0)
        d = result.to_dict()
        assert isinstance(d, dict)
        # Doit être sérialisable sans erreur
        json_str = json.dumps(d)
        assert len(json_str) > 0

    @pytest.mark.parametrize("temperature", [-51.0, 61.0])
    def test_temperature_invalide_leve_valueerror(self, predictor, temperature):
        """Une température hors plage doit lever ValueError."""
        with pytest.raises(ValueError):
            predictor.predict(temperature=temperature, humidite=50.0)

    @pytest.mark.parametrize("humidite", [-1.0, 101.0])
    def test_humidite_invalide_leve_valueerror(self, predictor, humidite):
        """Une humidité hors plage doit lever ValueError."""
        with pytest.raises(ValueError):
            predictor.predict(temperature=25.0, humidite=humidite)

    @pytest.mark.parametrize("temperature,humidite", [
        (-50.0, 0.0),    # limites basses
        (60.0, 100.0),   # limites hautes
        (0.0, 50.0),     # point zéro
        (36.6, 70.0),    # valeur typique
    ])
    def test_valeurs_limites_valides(self, predictor, temperature, humidite):
        """Les valeurs aux limites valides ne doivent pas lever d'exception."""
        result = predictor.predict(temperature=temperature, humidite=humidite)
        assert result is not None


class TestBioSensePredictorFromFile:
    """Tests du chargement depuis un fichier .pkl."""

    def test_fichier_introuvable_leve_filenotfounderror(self, tmp_path):
        """from_file() doit lever FileNotFoundError si le .pkl est absent."""
        with pytest.raises(FileNotFoundError, match="Modèle introuvable"):
            BioSensePredictor.from_file(str(tmp_path / "inexistant.pkl"))

    def test_model_info_retourne_dict(self, predictor):
        """model_info doit retourner un dictionnaire avec les clés attendues."""
        info = predictor.model_info
        assert isinstance(info, dict)
        assert "type" in info
        assert "n_estimators" in info
        assert "features" in info
        assert "n_classes" in info
