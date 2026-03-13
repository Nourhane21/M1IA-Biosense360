#!/usr/bin/env python3
"""
BioSense360 — Démonstration Interactive
========================================
Lance une démo complète du système sans serveur Flask.
Montre les prédictions sur 8 scénarios réels, de la chaleur normale
au danger extrême, avec la jauge Humidex et les protocoles de sécurité.

Usage :
    python demo.py
    python demo.py --scenario          # mode scénarios uniquement
    python demo.py --interactif        # entrer ses propres valeurs
"""

from __future__ import annotations
import argparse
import os
import sys
import time
from pathlib import Path

# ─── Répertoire courant = production/ ────────────────────────────────────────
os.chdir(Path(__file__).parent)
sys.path.insert(0, str(Path(__file__).parent))

try:
    from biosense360 import BioSensePredictor, calculer_humidex
    from biosense360.config import SYSTEME_ALARME
except ImportError as e:
    print(f"\n❌  Dépendances manquantes : {e}")
    print("    Exécutez d'abord :  pip install -r requirements.txt\n")
    sys.exit(1)

# ─── Constantes d'affichage ───────────────────────────────────────────────────
LARGEUR = 64
JAUGE_LARGEUR = 40

COULEURS_CONSOLE = {
    0: "\033[92m",   # vert vif
    1: "\033[93m",   # jaune
    2: "\033[33m",   # orange
    3: "\033[33m",   # orange foncé
    4: "\033[91m",   # rouge clair
    5: "\033[91m",   # rouge
    6: "\033[31m",   # rouge foncé
    7: "\033[31m",   # rouge foncé
}
RESET = "\033[0m"
GRAS  = "\033[1m"

# ─── 8 scénarios de démonstration ────────────────────────────────────────────
SCENARIOS = [
    {"label": "Bureau climatisé (hiver)",         "temperature": 19.0, "humidite": 45.0},
    {"label": "Printemps agréable",               "temperature": 22.0, "humidite": 55.0},
    {"label": "Journée ensoleillée",              "temperature": 28.0, "humidite": 60.0},
    {"label": "Canicule modérée",                 "temperature": 32.0, "humidite": 65.0},
    {"label": "Alerte chaleur (travail extérieur)","temperature": 36.0, "humidite": 70.0},
    {"label": "Canicule intense",                 "temperature": 39.0, "humidite": 75.0},
    {"label": "Urgence vitale (serre industrielle)","temperature": 43.0,"humidite": 80.0},
    {"label": "Danger extrême",                   "temperature": 47.0, "humidite": 85.0},
]


# ─── Helpers d'affichage ─────────────────────────────────────────────────────

def barre(titre: str, car: str = "═") -> None:
    print(f"\n{car * LARGEUR}")
    if titre:
        padding = (LARGEUR - len(titre) - 2) // 2
        print(f"{'':>{padding}} {titre} {'':>{padding}}")
        print(car * LARGEUR)


def jauge_humidex(hx: float) -> str:
    """Affiche une barre de progression Humidex (0 → 50)."""
    hx_clamped = max(0.0, min(50.0, hx))
    rempli = int(hx_clamped / 50.0 * JAUGE_LARGEUR)
    barre_str = "█" * rempli + "░" * (JAUGE_LARGEUR - rempli)
    return f"[{barre_str}] {hx:.1f}"


def afficher_resultat(result, label: str = "", delai: float = 0.0) -> None:
    info = SYSTEME_ALARME[result.classe]
    couleur = COULEURS_CONSOLE.get(result.classe, "")

    print(f"\n{'─' * LARGEUR}")
    if label:
        print(f"  📍  {GRAS}{label}{RESET}")
    print(f"  🌡️   Température : {result.temperature}°C  |  Humidité : {result.humidite}%")
    print(f"  💧  Humidex     : {jauge_humidex(result.humidex)}")
    print(f"\n  {couleur}{GRAS}{info.couleur}  NIVEAU {result.classe} — {result.niveau.upper()}{RESET}")
    print(f"  💡  {result.conseil}")
    print(f"\n  Protocole de sécurité :")
    for i, action in enumerate(result.protocole, 1):
        print(f"    {i}. {action}")
    print(f"{'─' * LARGEUR}")

    if delai:
        time.sleep(delai)


# ─── Modes de démo ────────────────────────────────────────────────────────────

def demo_scenarios(predictor: BioSensePredictor) -> None:
    """Affiche les prédictions pour les 8 scénarios de référence."""
    barre("BioSense360 — Démonstration des 8 Scénarios")
    print(f"\n  Modèle : Random Forest | {predictor.model_info['n_estimators']} arbres")
    print(f"  Indice : Humidex (Masterton & Richardson, 1979)")
    print(f"  Classes : 8 niveaux de vivabilité thermique\n")

    for i, scenario in enumerate(SCENARIOS, 1):
        print(f"\n  [{i}/8]", end="", flush=True)
        time.sleep(0.3)
        result = predictor.predict(
            temperature=scenario["temperature"],
            humidite=scenario["humidite"]
        )
        afficher_resultat(result, label=scenario["label"], delai=0.5)

    barre("Résumé des 8 Scénarios", car="─")
    print(f"\n  {'N°':<4} {'Scénario':<35} {'T°C':>5} {'HR%':>5} {'HX':>6}  {'Niveau'}")
    print(f"  {'─'*4} {'─'*35} {'─'*5} {'─'*5} {'─'*6}  {'─'*22}")
    for i, sc in enumerate(SCENARIOS):
        hx = calculer_humidex(sc["temperature"], sc["humidite"])
        result = predictor.predict(sc["temperature"], sc["humidite"])
        couleur = COULEURS_CONSOLE.get(result.classe, "")
        print(
            f"  {i+1:<4} {sc['label']:<35} {sc['temperature']:>5.1f} "
            f"{sc['humidite']:>5.0f} {hx:>6.1f}  "
            f"{couleur}{result.niveau}{RESET}"
        )
    print()


def demo_interactif(predictor: BioSensePredictor) -> None:
    """Mode interactif : l'utilisateur entre ses propres valeurs."""
    barre("BioSense360 — Mode Interactif")
    print("\n  Entrez vos mesures capteur pour obtenir une prédiction.")
    print("  Tapez 'q' pour quitter.\n")

    while True:
        try:
            t_str = input("  Température (°C) : ").strip()
            if t_str.lower() == 'q':
                break
            h_str = input("  Humidité relative (%) : ").strip()
            if h_str.lower() == 'q':
                break

            temperature = float(t_str.replace(',', '.'))
            humidite    = float(h_str.replace(',', '.'))

            result = predictor.predict(temperature=temperature, humidite=humidite)
            afficher_resultat(result)

        except ValueError:
            print("  ⚠️  Valeur non valide, réessayez.")
        except KeyboardInterrupt:
            break

    print("\n  Au revoir.\n")


# ─── Point d'entrée ───────────────────────────────────────────────────────────

def main() -> None:
    parser = argparse.ArgumentParser(
        description="BioSense360 — Démonstration du système de prédiction",
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    parser.add_argument("--interactif", action="store_true",
                        help="Mode interactif : entrer ses propres valeurs")
    parser.add_argument("--scenario", action="store_true",
                        help="Mode scénarios uniquement (défaut)")
    args = parser.parse_args()

    # Chargement du modèle
    model_path = Path("models/modele_rf.pkl")
    if not model_path.exists():
        print(f"\n❌  Modèle introuvable : {model_path}")
        print("    Exécutez d'abord le notebook (cellule d'export) ou copiez modele_rf.pkl dans models/")
        sys.exit(1)

    print(f"\n  Chargement du modèle...", end="", flush=True)
    predictor = BioSensePredictor.from_file(str(model_path))
    print(f" ✅\n")

    if args.interactif:
        demo_interactif(predictor)
    else:
        demo_scenarios(predictor)
        if not args.scenario:
            reponse = input("\n  Voulez-vous tester vos propres valeurs ? (o/n) : ").strip().lower()
            if reponse in ('o', 'oui', 'y', 'yes'):
                demo_interactif(predictor)


if __name__ == "__main__":
    main()
