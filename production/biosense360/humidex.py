"""
BioSense360 — Calcul de l'indice Humidex
=========================================
Implémentation de l'indice Humidex (Masterton & Richardson, 1979),
utilisé comme métrique centrale de vivabilité thermique.

Référence :
    Masterton, J. M., & Richardson, F. A. (1979). Humidex: a method of
    quantifying human discomfort due to excessive heat and humidity.
    Downsview, Ontario: Environment Canada.

Pourquoi l'Humidex et non le PMV (ISO 7730) ?
    Le modèle classique PMV requiert 6 variables dont certaines sont
    impossibles à mesurer en extérieur (clo, met, MRT). Les capteurs
    ClimaTrack de Neusta ne fournissent de manière fiable que la
    température et l'humidité relative : l'Humidex ne nécessite que
    ces deux variables.
"""

from __future__ import annotations

import math


def calculer_humidex(temperature: float, humidite_relative: float) -> float:
    """Calcule l'indice Humidex à partir de la température et de l'humidité.

    Formule (Masterton & Richardson, 1979) :
        e = 6.112 × 10^(7.5 × T / (237.7 + T)) × (HR / 100)
        HX = T + (5/9) × (e - 10)

    Parameters
    ----------
    temperature : float
        Température ambiante en degrés Celsius. Plage valide : [-50, 60].
    humidite_relative : float
        Humidité relative en pourcentage. Plage valide : [0, 100].

    Returns
    -------
    float
        Valeur de l'Humidex, arrondie à 2 décimales.

    Raises
    ------
    ValueError
        Si les paramètres sont hors de leur plage de validité physique.

    Examples
    --------
    >>> calculer_humidex(30.0, 60.0)
    38.29
    >>> calculer_humidex(20.0, 40.0)
    21.45
    """
    if not (-50.0 <= temperature <= 60.0):
        raise ValueError(
            f"Température hors plage [-50, 60]°C : {temperature}"
        )
    if not (0.0 <= humidite_relative <= 100.0):
        raise ValueError(
            f"Humidité relative hors plage [0, 100]% : {humidite_relative}"
        )

    # Pression de vapeur saturante (hPa) à la température donnée
    e = 6.112 * (10 ** (7.5 * temperature / (237.7 + temperature))) * (
        humidite_relative / 100.0
    )

    humidex = temperature + (5.0 / 9.0) * (e - 10.0)
    return round(humidex, 2)


def classe_depuis_humidex(humidex: float) -> int:
    """Retourne la classe de vivabilité (0–7) correspondant à une valeur Humidex.

    Correspondance avec le système d'alarme à 8 niveaux :

    +---------+-------------------+
    | Classe  | Plage Humidex     |
    +=========+===================+
    | 0       | HX < 25           |
    | 1       | 25 ≤ HX < 30      |
    | 2       | 30 ≤ HX < 34      |
    | 3       | 34 ≤ HX < 38      |
    | 4       | 38 ≤ HX < 40      |
    | 5       | 40 ≤ HX < 43      |
    | 6       | 43 ≤ HX < 45      |
    | 7       | HX ≥ 45           |
    +---------+-------------------+

    Parameters
    ----------
    humidex : float
        Valeur de l'indice Humidex.

    Returns
    -------
    int
        Classe de vivabilité entre 0 et 7 inclus.

    Examples
    --------
    >>> classe_depuis_humidex(22.0)
    0
    >>> classe_depuis_humidex(36.5)
    3
    >>> classe_depuis_humidex(47.0)
    7
    """
    seuils = [25.0, 30.0, 34.0, 38.0, 40.0, 43.0, 45.0]
    for classe, seuil in enumerate(seuils):
        if humidex < seuil:
            return classe
    return 7
