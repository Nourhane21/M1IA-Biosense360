# BioSense360 — Dockerfile
# ==========================
# Construit une image légère pour déployer l'API REST BioSense360.
#
# Usage :
#   docker build -t biosense360-api .
#   docker run -p 5000:5000 -v $(pwd)/models:/app/models biosense360-api
#
# Variables d'environnement disponibles :
#   BIOSENSE_HOST          Adresse d'écoute (défaut : 0.0.0.0)
#   BIOSENSE_PORT          Port d'écoute (défaut : 5000)
#   BIOSENSE_MODEL_PATH    Chemin vers le .pkl (défaut : /app/models/modele_rf.pkl)

# --- Image de base légère ---
FROM python:3.11-slim

# --- Métadonnées ---
LABEL maintainer="Equipe BioSense360 <biosense360@univ-toulouse.fr>"
LABEL description="API REST de prédiction de vivabilité thermique"
LABEL version="1.0.0"

# --- Répertoire de travail ---
WORKDIR /app

# --- Installation des dépendances système minimales ---
RUN apt-get update && apt-get install -y --no-install-recommends \
    curl \
    && rm -rf /var/lib/apt/lists/*

# --- Copie et installation des dépendances Python ---
# On copie requirements.txt en premier pour exploiter le cache Docker
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# --- Copie du code source ---
COPY biosense360/ ./biosense360/
COPY scripts/ ./scripts/

# --- Création du dossier models (le .pkl sera monté en volume) ---
RUN mkdir -p /app/models

# --- Utilisateur non-root pour la sécurité ---
RUN useradd --create-home --shell /bin/bash biosense
USER biosense

# --- Configuration par défaut ---
ENV BIOSENSE_HOST=0.0.0.0
ENV BIOSENSE_PORT=5000
ENV BIOSENSE_MODEL_PATH=/app/models/modele_rf.pkl

# --- Port exposé ---
EXPOSE 5000

# --- Healthcheck ---
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
  CMD curl -f http://localhost:5000/health || exit 1

# --- Commande de démarrage ---
CMD ["python", "-m", "biosense360.api"]
