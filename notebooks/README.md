# BioSense360 — Notebook d'Analyse

> **TER Master 1 IA — Université de Toulouse**
> **Client :** Neusta (Damien Appert)
> **Équipe :** Nourhane Mallek · Soufiane Khallouki · Daniil Zhdanov

---

## Présentation

Le notebook `BioSense360_Pipeline_IA_v3.ipynb` constitue le cœur scientifique du projet.
Il implémente un pipeline de traitement et d'analyse des données environnementales
(température, humidité) collectées par les capteurs Neusta ClimaTrack.

---

## Partie 1 — Acquisition et Préparation des Données

Chargement, nettoyage et standardisation des deux sources de données :

| Cellule | Contenu |
|---------|---------|
| 1.1 | Chargement des jeux de données (Météo France + Neusta ClimaTrack) |
| 1.2 | Sélection et standardisation des colonnes |
| 1.3 | Nettoyage, contrôle qualité et filtrage |

**Sources :**
- `Data/meteo_France_data/` — relevés synoptiques Toulouse-Blagnac 2024–2025
- `Data/Neusta/` — 487 fichiers JSON capteurs industriels (2024-09-20 → 2026-02-19)

**Résultats :**
- 461 341 observations nettoyées (Météo France)
- 487 fichiers Neusta chargés (2 formats détectés automatiquement)
- Colonnes produites : `temperature` (°C), `humidite` (%), `humidex` (float), `classe` (int)

> ⚠️ Les fichiers CSV bruts Météo France (`synop_2024.csv`, `synop_2025.csv`) ne sont pas versionnés en raison de leur taille (> 50 MB).

---

## Prérequis

```bash
pip install pandas numpy scikit-learn matplotlib seaborn jupyter joblib
```

## Exécution

```bash
jupyter notebook notebooks/BioSense360_Pipeline_IA_v3.ipynb
```

Les cellules sont conçues pour être exécutées séquentiellement.
