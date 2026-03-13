"""
BioSense360 — Moteur de prédiction
====================================
Encapsule le chargement du modèle Random Forest et la logique de prédiction.
Conçu pour être utilisé aussi bien dans l'API REST que dans les scripts
de surveillance temps réel.

Usage minimal :
    >>> predictor = BioSensePredictor.from_file("models/modele_rf.pkl")
    >>> result = predictor.predict(temperature=35.0, humidite=70.0)
    >>> print(result.niveau)  # "Inconfort évident"
"""

from __future__ import annotations

import logging
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path
from typing import List

import joblib
import pandas as pd

from .config import DEFAULT_MODEL_PATH, MODEL_FEATURES, SYSTEME_ALARME, NiveauAlarme
from .humidex import calculer_humidex

logger = logging.getLogger(__name__)


# ---------------------------------------------------------------------------
# Résultat de prédiction
# ---------------------------------------------------------------------------


@dataclass(frozen=True)
class PredictionResult:
    """Résultat complet d'une prédiction BioSense360.

    Attributes
    ----------
    timestamp : str
        Horodatage ISO 8601 de la prédiction.
    temperature : float
        Température d'entrée (°C).
    humidite : float
        Humidité relative d'entrée (%).
    humidex : float
        Valeur Humidex calculée.
    classe : int
        Classe de vivabilité prédite (0–7).
    seuil : str
        Description de la plage Humidex correspondante.
    niveau : str
        Intitulé du niveau d'alarme.
    conseil : str
        Recommandation courte.
    protocole : List[str]
        Actions de sécurité détaillées.
    """

    timestamp: str
    temperature: float
    humidite: float
    humidex: float
    classe: int
    seuil: str
    niveau: str
    conseil: str
    protocole: List[str]

    def to_dict(self) -> dict:
        """Sérialise le résultat en dictionnaire JSON-compatible."""
        return {
            "timestamp": self.timestamp,
            "entree": {
                "temperature": self.temperature,
                "humidite": self.humidite,
            },
            "humidex": self.humidex,
            "classe": self.classe,
            "seuil": self.seuil,
            "niveau": self.niveau,
            "conseil": self.conseil,
            "protocole": self.protocole,
        }


# ---------------------------------------------------------------------------
# Moteur de prédiction
# ---------------------------------------------------------------------------


class BioSensePredictor:
    """Moteur de prédiction de vivabilité thermique BioSense360.

    Encapsule un modèle scikit-learn (Random Forest) et fournit une
    interface haut-niveau pour la prédiction à partir des données capteurs.

    Parameters
    ----------
    model : object
        Modèle scikit-learn chargé (doit implémenter `.predict()`).
    model_path : str
        Chemin d'origine du modèle (pour logging/tracabilité).
    """

    def __init__(self, model: object, model_path: str = "inconnu") -> None:
        self._model = model
        self._model_path = model_path
        logger.info(
            "BioSensePredictor initialisé — modèle : %s (%d arbres)",
            model_path,
            getattr(model, "n_estimators", "?"),
        )

    # ------------------------------------------------------------------
    # Constructeurs alternatifs
    # ------------------------------------------------------------------

    @classmethod
    def from_file(cls, model_path: str = DEFAULT_MODEL_PATH) -> "BioSensePredictor":
        """Charge le modèle depuis un fichier .pkl et retourne un prédicateur.

        Parameters
        ----------
        model_path : str
            Chemin vers le fichier .pkl généré par le notebook.

        Returns
        -------
        BioSensePredictor

        Raises
        ------
        FileNotFoundError
            Si le fichier modèle n'existe pas à l'emplacement indiqué.
        """
        path = Path(model_path)
        if not path.exists():
            raise FileNotFoundError(
                f"Modèle introuvable : {model_path}\n"
                f"Exécutez d'abord la cellule 7.1 du notebook pour générer le fichier."
            )

        model = joblib.load(path)
        logger.info("Modèle chargé depuis %s", path.resolve())
        return cls(model=model, model_path=str(path.resolve()))

    # ------------------------------------------------------------------
    # Prédiction
    # ------------------------------------------------------------------

    def predict(self, temperature: float, humidite: float) -> PredictionResult:
        """Prédit la classe de vivabilité et retourne un rapport complet.

        Parameters
        ----------
        temperature : float
            Température ambiante en °C. Plage valide : [-50, 60].
        humidite : float
            Humidité relative en %. Plage valide : [0, 100].

        Returns
        -------
        PredictionResult
            Rapport complet avec classe, Humidex, niveau et protocole.

        Raises
        ------
        ValueError
            Si les paramètres sont hors plage physique.

        Examples
        --------
        >>> predictor = BioSensePredictor.from_file("models/modele_rf.pkl")
        >>> result = predictor.predict(temperature=38.0, humidite=70.0)
        >>> result.classe
        4
        """
        self._validate_inputs(temperature, humidite)

        donnee = pd.DataFrame(
            {"temperature": [temperature], "humidite": [humidite]}
        )
        classe = int(self._model.predict(donnee)[0])
        hx = calculer_humidex(temperature, humidite)
        info: NiveauAlarme = SYSTEME_ALARME[classe]

        logger.debug(
            "Prédiction : T=%.1f°C HR=%.0f%% → HX=%.2f → Classe %d (%s)",
            temperature, humidite, hx, classe, info.niveau,
        )

        return PredictionResult(
            timestamp=datetime.now().isoformat(),
            temperature=temperature,
            humidite=humidite,
            humidex=hx,
            classe=classe,
            seuil=info.seuil,
            niveau=info.niveau,
            conseil=info.conseil,
            protocole=list(info.protocole),
        )

    # ------------------------------------------------------------------
    # Propriétés
    # ------------------------------------------------------------------

    @property
    def model_info(self) -> dict:
        """Retourne les informations de configuration du modèle."""
        return {
            "type": type(self._model).__name__,
            "n_estimators": getattr(self._model, "n_estimators", None),
            "criterion": getattr(self._model, "criterion", None),
            "features": MODEL_FEATURES,
            "n_classes": len(SYSTEME_ALARME),
            "model_path": self._model_path,
        }

    # ------------------------------------------------------------------
    # Validation interne
    # ------------------------------------------------------------------

    @staticmethod
    def _validate_inputs(temperature: float, humidite: float) -> None:
        """Lève ValueError si les entrées sont hors plage."""
        if not (-50.0 <= temperature <= 60.0):
            raise ValueError(
                f"Température hors plage [-50, 60]°C : {temperature}"
            )
        if not (0.0 <= humidite <= 100.0):
            raise ValueError(
                f"Humidité relative hors plage [0, 100]% : {humidite}"
            )
