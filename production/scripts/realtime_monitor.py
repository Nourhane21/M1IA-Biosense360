#!/usr/bin/env python3
"""
BioSense360 — Script de surveillance en temps réel
=====================================================
Simule ou connecte un capteur ClimaTrack Neusta et génère des alertes
de vivabilité en continu, avec journalisation CSV.

En production, remplacer `SensorAdapter` par l'adaptateur Neusta réel
(MQTT, API REST, ou lecture série selon votre infrastructure).

Usage :
    python realtime_monitor.py                    # Mode simulation (par défaut)
    python realtime_monitor.py --iterations 50    # 50 lectures
    python realtime_monitor.py --interval 10      # Intervalle 10 secondes
    python realtime_monitor.py --log alerts.csv   # Fichier de journalisation
    python realtime_monitor.py --help             # Aide complète

Variables d'environnement :
    BIOSENSE_MODEL_PATH   Chemin vers le fichier .pkl du modèle
"""

from __future__ import annotations

import argparse
import csv
import logging
import random
import sys
import time
from abc import ABC, abstractmethod
from datetime import datetime
from pathlib import Path
from typing import Iterator

# Ajout du répertoire parent dans sys.path pour l'exécution en standalone
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from biosense360 import BioSensePredictor
from biosense360.predictor import PredictionResult

logger = logging.getLogger(__name__)


# ---------------------------------------------------------------------------
# Interface capteur (Pattern Adapter)
# ---------------------------------------------------------------------------


class SensorReading:
    """Lecture brute d'un capteur environnemental."""

    __slots__ = ("temperature", "humidite", "timestamp")

    def __init__(self, temperature: float, humidite: float) -> None:
        self.temperature = temperature
        self.humidite = humidite
        self.timestamp = datetime.now()


class SensorAdapter(ABC):
    """Interface abstraite pour les capteurs BioSense360.

    Pour connecter un vrai capteur Neusta ClimaTrack, créez une sous-classe
    et implémentez `read()` selon votre protocole (MQTT, REST, série...).
    """

    @abstractmethod
    def read(self) -> SensorReading:
        """Retourne une lecture capteur."""
        ...

    def stream(self, interval_sec: float = 10.0) -> Iterator[SensorReading]:
        """Génère un flux continu de lectures à intervalle régulier."""
        while True:
            yield self.read()
            time.sleep(interval_sec)


class SimulatedSensor(SensorAdapter):
    """Capteur simulé — variation diurne réaliste + bruit gaussien.

    Modélise une journée type avec :
    - Courbe de température sinusoïdale (min ~15°C, max ~30°C)
    - Humidité relative inversement corrélée à la température
    - Bruit gaussien pour simuler les fluctuations réelles
    """

    def read(self) -> SensorReading:
        # Simule les heures via les secondes pour la démo
        heure = datetime.now().second % 24
        base_temp = 15.0 + 15.0 * (
            (1 - (abs(heure - 14) / 14)) if heure <= 14
            else (1 - ((heure - 14) / 10))
        )
        temperature = round(base_temp + random.gauss(0, 1.5), 1)
        humidite = round(
            max(20.0, min(95.0, 70.0 - 0.5 * temperature + random.gauss(0, 4))),
            0,
        )
        return SensorReading(temperature=temperature, humidite=humidite)


# ---------------------------------------------------------------------------
# Journalisation CSV
# ---------------------------------------------------------------------------


class AlertLogger:
    """Journalise les résultats de prédiction dans un fichier CSV.

    Parameters
    ----------
    path : str | Path
        Chemin du fichier CSV de sortie.
    """

    FIELDNAMES = [
        "timestamp", "temperature", "humidite",
        "humidex", "classe", "niveau", "conseil",
    ]

    def __init__(self, path: str | Path) -> None:
        self._path = Path(path)
        self._file = self._path.open("w", newline="", encoding="utf-8")
        self._writer = csv.DictWriter(self._file, fieldnames=self.FIELDNAMES)
        self._writer.writeheader()
        logger.info("Journal d'alertes ouvert : %s", self._path.resolve())

    def log(self, result: PredictionResult) -> None:
        """Ajoute une ligne de résultat au journal."""
        self._writer.writerow({
            "timestamp": result.timestamp,
            "temperature": result.temperature,
            "humidite": result.humidite,
            "humidex": result.humidex,
            "classe": result.classe,
            "niveau": result.niveau,
            "conseil": result.conseil,
        })
        self._file.flush()

    def close(self) -> None:
        """Ferme proprement le fichier CSV."""
        self._file.close()
        logger.info("Journal fermé : %s", self._path)

    def __enter__(self) -> "AlertLogger":
        return self

    def __exit__(self, *_) -> None:
        self.close()


# ---------------------------------------------------------------------------
# Affichage console
# ---------------------------------------------------------------------------


def afficher_rapport(result: PredictionResult) -> None:
    """Affiche un rapport de prédiction formaté dans la console."""
    from biosense360.config import SYSTEME_ALARME

    info = SYSTEME_ALARME[result.classe]
    separateur = "─" * 60

    print(f"\n{separateur}")
    print(f"  📡  {result.timestamp}")
    print(
        f"  Capteur  : {result.temperature}°C | "
        f"{result.humidite}% HR | Humidex = {result.humidex}"
    )
    print(f"  {info.couleur}  Niveau {result.classe} — {result.niveau}")
    print(f"  💡  {result.conseil}")
    print(separateur)


# ---------------------------------------------------------------------------
# Boucle principale de surveillance
# ---------------------------------------------------------------------------


def run_monitor(
    sensor: SensorAdapter,
    predictor: BioSensePredictor,
    iterations: int,
    interval_sec: float,
    log_path: str | Path,
) -> None:
    """Exécute la boucle de surveillance.

    Parameters
    ----------
    sensor : SensorAdapter
        Adaptateur capteur (simulé ou réel).
    predictor : BioSensePredictor
        Moteur de prédiction chargé.
    iterations : int
        Nombre de lectures à effectuer (0 = infini).
    interval_sec : float
        Délai en secondes entre deux lectures.
    log_path : str | Path
        Fichier CSV de journalisation.
    """
    print("\n" + "=" * 60)
    print("   BIOSENSE360 — Surveillance Environnementale Active")
    print("=" * 60)
    print(f"  Mode       : {'Simulation' if isinstance(sensor, SimulatedSensor) else 'Capteur réel'}")
    print(f"  Lectures   : {iterations if iterations > 0 else '∞ (continu)'}")
    print(f"  Intervalle : {interval_sec}s")
    print(f"  Journal    : {log_path}")
    print("=" * 60)

    count = 0
    with AlertLogger(log_path) as alert_logger:
        try:
            for reading in sensor.stream(interval_sec=interval_sec):
                result = predictor.predict(
                    temperature=reading.temperature,
                    humidite=reading.humidite,
                )
                afficher_rapport(result)
                alert_logger.log(result)

                count += 1
                if iterations > 0 and count >= iterations:
                    break

        except KeyboardInterrupt:
            print("\n\n[SYSTÈME] Arrêt demandé par l'opérateur.")

    print(f"\n[JOURNAL] {count} événement(s) sauvegardés → {log_path}\n")


# ---------------------------------------------------------------------------
# Interface ligne de commande
# ---------------------------------------------------------------------------


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="BioSense360 — Surveillance de vivabilité en temps réel",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Exemples :
  python realtime_monitor.py
  python realtime_monitor.py --iterations 20 --interval 2
  python realtime_monitor.py --log /tmp/alertes.csv
        """,
    )
    parser.add_argument(
        "--model",
        default=None,
        metavar="PATH",
        help="Chemin vers le fichier .pkl du modèle (défaut : BIOSENSE_MODEL_PATH ou models/modele_rf.pkl)",
    )
    parser.add_argument(
        "--iterations",
        type=int,
        default=10,
        metavar="N",
        help="Nombre de lectures à effectuer (0 = continu, défaut : 10)",
    )
    parser.add_argument(
        "--interval",
        type=float,
        default=1.0,
        metavar="SEC",
        help="Intervalle entre deux lectures en secondes (défaut : 1.0)",
    )
    parser.add_argument(
        "--log",
        default="journal_alertes.csv",
        metavar="PATH",
        help="Fichier CSV de journalisation (défaut : journal_alertes.csv)",
    )
    parser.add_argument(
        "--verbose",
        action="store_true",
        help="Affiche les messages de débogage",
    )
    return parser.parse_args()


def main() -> None:
    args = parse_args()

    logging.basicConfig(
        level=logging.DEBUG if args.verbose else logging.WARNING,
        format="%(asctime)s [%(levelname)s] %(name)s — %(message)s",
    )

    predictor = BioSensePredictor.from_file(
        args.model or str(
            Path(__file__).resolve().parent.parent / "models" / "modele_rf.pkl"
        )
    )

    sensor = SimulatedSensor()
    # Pour un capteur réel, remplacer par votre adaptateur :
    # sensor = NeustaClimaTrackAdapter(host="192.168.1.x", topic="capteur/data")

    run_monitor(
        sensor=sensor,
        predictor=predictor,
        iterations=args.iterations,
        interval_sec=args.interval,
        log_path=args.log,
    )


if __name__ == "__main__":
    main()
