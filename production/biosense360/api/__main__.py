"""Point d'entrée pour `python -m biosense360.api`."""

from .app import create_app
from ..config import API_HOST, API_PORT, API_DEBUG
import logging

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s — %(message)s",
)

print()
print("  ╔══════════════════════════════════════════════════╗")
print("  ║      BioSense360 — API de Vivabilité Active      ║")
print("  ╠══════════════════════════════════════════════════╣")
print("  ║  GET  /health   → État du service + modèle       ║")
print("  ║  POST /predict  → Prédiction temps réel          ║")
print("  ║  GET  /seuils   → Seuils critiques Humidex       ║")
print("  ╚══════════════════════════════════════════════════╝")
print()

app = create_app()
app.run(host=API_HOST, port=API_PORT, debug=API_DEBUG)
