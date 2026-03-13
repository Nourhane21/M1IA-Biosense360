"""
BioSense360 — Configuration des tests pytest
=============================================
Fixtures partagées entre tous les modules de tests.
"""

from __future__ import annotations

import sys
from pathlib import Path
from unittest.mock import MagicMock

import numpy as np
import pytest

# Assure que le package biosense360 est importable depuis les tests
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from biosense360.config import SYSTEME_ALARME
from biosense360.predictor import BioSensePredictor


# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------


@pytest.fixture(scope="session")
def mock_model():
    """Modèle scikit-learn simulé (sans fichier .pkl requis).

    Retourne la classe 0 pour T < 25, la classe 4 pour T ≥ 35,
    ce qui suffit pour tester la logique applicative.
    """
    model = MagicMock()
    model.n_estimators = 500
    model.criterion = "entropy"

    def side_effect(df):
        temp = df["temperature"].iloc[0]
        if temp >= 45:
            return np.array([7])
        elif temp >= 43:
            return np.array([6])
        elif temp >= 40:
            return np.array([5])
        elif temp >= 38:
            return np.array([4])
        elif temp >= 34:
            return np.array([3])
        elif temp >= 30:
            return np.array([2])
        elif temp >= 25:
            return np.array([1])
        else:
            return np.array([0])

    model.predict.side_effect = side_effect
    return model


@pytest.fixture(scope="session")
def predictor(mock_model):
    """BioSensePredictor utilisant le modèle simulé."""
    return BioSensePredictor(model=mock_model, model_path="test_mock")


@pytest.fixture(scope="session")
def flask_client(predictor):
    """Client Flask de test."""
    from biosense360.api.app import create_app

    # On injecte directement le predictor pour ne pas avoir besoin du .pkl
    app = create_app.__wrapped__ if hasattr(create_app, "__wrapped__") else None
    # Création manuelle de l'app avec injection du predictor simulé
    from flask import Flask
    from biosense360.api.app import _register_routes

    test_app = Flask(__name__)
    test_app.config["PREDICTOR"] = predictor
    _register_routes(test_app)
    test_app.config["TESTING"] = True

    with test_app.test_client() as client:
        yield client
