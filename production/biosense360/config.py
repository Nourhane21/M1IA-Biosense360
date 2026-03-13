"""
BioSense360 — Configuration et constantes métier
=================================================
Centralise toutes les constantes du projet : système d'alarme Humidex
(8 niveaux) et protocoles de recommandation humaine (F3 / F4).

Fondements scientifiques des seuils et protocoles :
    - Alfano, F. R. d'A. et al. (2010). Thermal comfort in outdoor
      environments. ASHRAE Transactions.
    - OHCOW (2022). Heat Stress Humidex-Based Guideline for Ontario
      Workplaces. Occupational Health Clinics for Ontario Workers.
    - NIOSH (2016). Criteria for a Recommended Standard: Occupational
      Exposure to Heat and Hot Environments. DHHS Pub. n° 2016-106.
    - ACGIH (2023). TLV for Heat Stress and Heat Strain.
    - Bouchama & Knochel (2002). Heat stroke. NEJM 346(25):1978-1988.
    - HAS (2023). Prise en charge du coup de chaleur d'exercice.
    - Décret n° 2025-482 — obligations employeur chaleur (FR, 01/07/2025).

Protocoles hydratation (NIOSH/OSHA) :
    Effort modéré  : 240–250 mL toutes les 20 min (~0.75 L/h)
    Effort intense : 240 mL toutes les 15 min (~1.0 L/h)
    Plafond absolu : 1.5 L/h (au-delà : risque hyponatrémie)

Cycles travail-repos (ACGIH TLV / OHCOW) :
    Humidex 38–40 : 45 min travail / 15 min repos
    Humidex 40–43 : 30 min travail / 30 min repos
    Humidex 43–45 : 15 min travail / 45 min repos
    Humidex ≥ 45  : arrêt total
"""

from __future__ import annotations

import os
from dataclasses import dataclass, field
from typing import Dict, List

# ---------------------------------------------------------------------------
# Features attendues par le modèle
# ---------------------------------------------------------------------------

MODEL_FEATURES: List[str] = ["temperature", "humidite"]

# ---------------------------------------------------------------------------
# Système d'alarme Humidex — 8 niveaux (Alfano et al., 2010)
# ---------------------------------------------------------------------------


@dataclass(frozen=True)
class NiveauAlarme:
    """Représente un niveau d'alarme Humidex."""

    seuil: str
    """Plage d'Humidex correspondante (ex: '34 ≤ HX < 38')."""

    niveau: str
    """Intitulé du niveau (ex: 'Inconfort évident')."""

    conseil: str
    """Recommandation courte pour l'utilisateur final."""

    protocole: List[str]
    """Liste ordonnée des actions de sécurité."""

    couleur: str
    """Code couleur associé (pour l'affichage console / UI)."""


SYSTEME_ALARME: Dict[int, NiveauAlarme] = {
    # Classe 0 — OMS : apport hydrique standard adulte actif
    0: NiveauAlarme(
        seuil="HX < 25",
        niveau="Conditions Normales",
        conseil="Conditions idéales. Aucune restriction.",
        protocole=[
            "Aucune mesure de protection requise.",
            "Hydratation habituelle (~1,5 L/jour).",
        ],
        couleur="🟢",
    ),
    # Classe 1 — OHCOW Level 1 : sensibilisation préventive
    1: NiveauAlarme(
        seuil="25 ≤ HX < 30",
        niveau="Gêne légère",
        conseil="Hydratez-vous normalement lors d'efforts.",
        protocole=[
            "200 mL d'eau fraîche toutes les 30 min d'effort.",
            "Vêtements légers, clairs et respirants.",
        ],
        couleur="🟡",
    ),
    # Classe 2 — OHCOW Level 2 ; NIOSH : 0.75 L/h (effort modéré)
    2: NiveauAlarme(
        seuil="30 ≤ HX < 34",
        niveau="Vigilance",
        conseil="Buvez régulièrement. Réduisez les efforts au soleil.",
        protocole=[
            "Surveillance horaire de T° et HR.",
            "250 mL d'eau fraîche toutes les 20 min.",
            "Réduire les efforts intenses entre 12h et 16h.",
        ],
        couleur="🟠",
    ),
    # Classe 3 — OHCOW Level 3 ; INRS fiche R-447
    3: NiveauAlarme(
        seuil="34 ≤ HX < 38",
        niveau="Inconfort évident",
        conseil="Hydratation active obligatoire. Privilégiez l'ombre.",
        protocole=[
            "250 mL d'eau fraîche toutes les 20 min.",
            "Pause à l'ombre : 10 min minimum par heure.",
            "Reporter les travaux lourds avant 10h ou après 18h.",
        ],
        couleur="🟠",
    ),
    # Classe 4 — ACGIH TLV : 45 min travail / 15 min repos (effort modéré)
    #            Décret n° 2025-482 : évaluation DUERP obligatoire
    4: NiveauAlarme(
        seuil="38 ≤ HX < 40",
        niveau="Alerte",
        conseil="15 min de repos par heure. Travaux lourds suspendus.",
        protocole=[
            "Cycle obligatoire : 45 min travail / 15 min repos (ACGIH TLV).",
            "240 mL d'eau fraîche toutes les 20 min.",
            "Système de binôme obligatoire — aucun travailleur isolé.",
            "Kit premiers secours chaleur accessible sur site.",
        ],
        couleur="🔴",
    ),
    # Classe 5 — ACGIH TLV : 30 min travail / 30 min repos
    #            OHCOW Level 5 ; retrait des populations vulnérables
    5: NiveauAlarme(
        seuil="40 ≤ HX < 43",
        niveau="Inconfort intense",
        conseil="Arrêt des efforts non essentiels. 30 min repos/heure minimum.",
        protocole=[
            "Cycle obligatoire : 30 min travail / 30 min repos (ACGIH TLV).",
            "250 mL d'eau fraîche toutes les 15 min + électrolytes.",
            "Rafraîchissement actif : brumisateurs, linges humides.",
            "Cessation immédiate au moindre symptôme (vertiges, confusion, nausées).",
        ],
        couleur="🔴",
    ),
    # Classe 6 — ACGIH TLV : 15 min travail / 45 min repos
    #            OHCOW Level 6 ; Décret 2025-482 : arrêt possible par DREETS
    6: NiveauAlarme(
        seuil="43 ≤ HX < 45",
        niveau="Urgence Vitale",
        conseil="Tous travaux extérieurs proscrits. Rester dans un espace frais.",
        protocole=[
            "AUCUNE activité physique extérieure.",
            "Cycle max : 15 min activité légère / 45 min repos en espace frais (< 26 °C).",
            "Vérification état de santé (conscience, sudation) chaque heure.",
            "SAMU (15) accessible immédiatement — numéro affiché sur chaque poste.",
        ],
        couleur="🚨",
    ),
    # Classe 7 — OHCOW Level 7 : arrêt total (medically supervised work only)
    #            HAS (2023) : protocole coup de chaleur ; mortalité 10-50 % sans PEC
    7: NiveauAlarme(
        seuil="HX ≥ 45",
        niveau="Danger Extrême",
        conseil="SUSPENSION IMMÉDIATE de toute activité. Risque vital.",
        protocole=[
            "SUSPENSION TOTALE de toute activité physique.",
            "Environnement climatisé obligatoire (< 24 °C) et surveillance continue.",
            "SAMU (15) au moindre signe : confusion, absence de sueur, T° > 39.5 °C.",
            "En cas de coup de chaleur : refroidir immédiatement (linges froids cou/aines/aisselles).",
        ],
        couleur="🚨",
    ),
}

# ---------------------------------------------------------------------------
# Paramètres de l'API (surchargeable via variables d'environnement)
# ---------------------------------------------------------------------------

API_HOST: str = os.getenv("BIOSENSE_HOST", "0.0.0.0")
API_PORT: int = int(os.getenv("BIOSENSE_PORT", "5000"))
API_DEBUG: bool = os.getenv("BIOSENSE_DEBUG", "false").lower() == "true"

# ---------------------------------------------------------------------------
# Chemins par défaut (relatifs au dossier production/)
# ---------------------------------------------------------------------------

DEFAULT_MODEL_PATH: str = os.getenv(
    "BIOSENSE_MODEL_PATH",
    os.path.join(os.path.dirname(__file__), "..", "models", "modele_rf.pkl"),
)
