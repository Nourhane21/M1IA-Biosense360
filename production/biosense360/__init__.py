"""
BioSense360 — Package de prédiction de vivabilité thermique
============================================================
TER Master 1 IA — Université de Toulouse
Client : Neusta (Damien Appert) | Encadrant : Pr. Gilles Lépinard
Équipe : Nourhane MALLEK · Soufiane KHALLOUKI · Daniil ZHDANOV
"""

from .humidex import calculer_humidex, classe_depuis_humidex
from .predictor import BioSensePredictor, PredictionResult

__all__ = [
    "BioSensePredictor",
    "PredictionResult",
    "calculer_humidex",
    "classe_depuis_humidex",
]

__version__ = "1.0.0"
__author__ = "Équipe BioSense360"
