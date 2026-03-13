# BioSense360 — Module Production

Ce module contient le code Python prêt pour le déploiement en production.
Il est **indépendant du notebook** : une fois le modèle `.pkl` exporté, ce module
peut fonctionner de façon autonome.

---

## Installation

```bash
cd production
pip install -r requirements.txt
```

> **Prérequis :** Python 3.9+ et le fichier `models/modele_rf.pkl` généré par le notebook.

---

## Utilisation

### API REST (mode recommandé)

```bash
python -m biosense360.api
# → Service disponible sur http://localhost:5000
```

| Méthode | Endpoint | Description |
|---------|----------|-------------|
| `GET` | `/health` | Santé du service + infos modèle |
| `POST` | `/predict` | Prédiction depuis `{temperature, humidite}` |
| `GET` | `/seuils` | Tableau des 8 seuils critiques |

**Exemple :**
```bash
curl -X POST http://localhost:5000/predict \
  -H "Content-Type: application/json" \
  -d '{"temperature": 35.0, "humidite": 70}'
```

### Surveillance temps réel (CLI)

```bash
python scripts/realtime_monitor.py --iterations 20 --interval 2
python scripts/realtime_monitor.py --help  # toutes les options
```

### Utilisation comme bibliothèque Python

```python
from biosense360 import BioSensePredictor

predictor = BioSensePredictor.from_file("models/modele_rf.pkl")
result = predictor.predict(temperature=35.0, humidite=70.0)

print(result.niveau)    # "Inconfort évident"
print(result.humidex)   # 44.87
print(result.protocole) # ["250 mL d'eau...", ...]
```

---

## Tests

```bash
pytest tests/ -v
pytest tests/ -v --cov=biosense360  # avec couverture
```

---

## Docker

```bash
# Construction
docker build -t biosense360-api .

# Lancement (monte le modèle en volume)
docker run -p 5000:5000 \
  -v $(pwd)/models:/app/models \
  biosense360-api
```

---

## Structure

```
production/
├── biosense360/
│   ├── __init__.py        Exports publics du package
│   ├── config.py          Constantes : SYSTEME_ALARME, paramètres API
│   ├── humidex.py         Calcul Humidex (Masterton & Richardson, 1979)
│   ├── predictor.py       BioSensePredictor + PredictionResult
│   └── api/
│       ├── __init__.py
│       └── app.py         Application Factory Flask
├── scripts/
│   └── realtime_monitor.py  Surveillance CLI avec Pattern Adapter capteur
├── tests/
│   ├── conftest.py          Fixtures partagées (mock model)
│   ├── test_humidex.py      Tests calcul Humidex
│   ├── test_predictor.py    Tests du moteur de prédiction
│   └── test_api.py          Tests des 3 endpoints REST
├── models/
│   └── .gitkeep             modele_rf.pkl à placer ici (non versionné)
├── requirements.txt
├── Dockerfile
└── .env.example
```

---

## Variables d'environnement

| Variable | Défaut | Description |
|----------|--------|-------------|
| `BIOSENSE_HOST` | `0.0.0.0` | Adresse d'écoute de l'API |
| `BIOSENSE_PORT` | `5000` | Port de l'API |
| `BIOSENSE_DEBUG` | `false` | Mode debug Flask |
| `BIOSENSE_MODEL_PATH` | `./models/modele_rf.pkl` | Chemin vers le modèle |

Copier `.env.example` en `.env` et adapter les valeurs.
