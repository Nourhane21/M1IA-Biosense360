# BioSense360 — Notebook d'Analyse

> **TER Master 1 IA — Université de Toulouse**
> **Client :** Neusta (Damien Appert)
> **Équipe :** Nourhane Mallek · Soufiane Khallouki · Daniil Zhdanov

---

## Présentation

Le notebook `BioSense360_Pipeline_IA_v3.ipynb` constitue le cœur scientifique du projet BioSense360.
Il couvre l'intégralité du pipeline IA : acquisition des données, modélisation prédictive,
détection des dangers thermiques et génération de recommandations de sécurité.

---

## Partie 1 — Acquisition et Préparation des Données

| Cellule | Contenu |
|---------|---------|
| 1.1 | Chargement des jeux de données (Météo France + Neusta ClimaTrack) |
| 1.2 | Sélection et standardisation des colonnes |
| 1.3 | Nettoyage, contrôle qualité et filtrage |

**Sources :**
- `Data/meteo_France_data/` — relevés Toulouse-Blagnac 2024–2025 (461 341 obs.)
- `Data/Neusta/` — 487 fichiers JSON capteurs (2024-09 → 2026-02)

> ⚠️ Les fichiers bruts `synop_2024.csv` / `synop_2025.csv` ne sont pas versionnés (> 50 MB).

---

## Partie 2 — Modélisation et Prédiction

| Modèle | Accuracy (test 20 %) | Validation croisée 5-fold |
|--------|--------------------|--------------------------|
| Random Forest (500 arbres, Entropie) | **99,98 %** | **99,96 % ± 0,04 %** |
| Gradient Boosting | 99,74 % | — |
| Régression Logistique | 97,22 % | — |

> ⚠️ Le modèle `modele_rf.pkl` n'est pas versionné (> 100 MB). À générer via le notebook.

---

## Partie 3 — Détection des Dangers Thermiques

| Classe | Seuil HX | Niveau |
|--------|----------|--------|
| 0 | < 25 | Conditions normales |
| 1 | 25–30 | Gêne légère |
| 2 | 30–34 | Vigilance |
| 3 | 34–38 | Inconfort évident |
| 4 | 38–40 | Alerte |
| 5 | 40–43 | Inconfort intense |
| 6 | 43–45 | Urgence vitale |
| 7 | ≥ 45 | Danger extrême |

**Validation sur capteurs réels Neusta : 99,05 % d'accuracy.**

---

## Partie 4 — Recommandations de Sécurité Thermique

Pipeline complet : capteur → prédiction IA → alerte → protocole de sécurité.
Protocoles référencés : INRS, NIOSH, OHCOW, Décret 2025-482.

---

## Résultats clés

| Indicateur | Valeur | Objectif |
|------------|--------|----------|
| Accuracy Random Forest (test) | **99,98 %** | ≥ 95 % ✅ |
| Accuracy Gradient Boosting | **99,74 %** | ≥ 95 % ✅ |
| Validation croisée 5-fold | **99,96 % ± 0,04 %** | ≥ 95 % ✅ |
| Validation capteurs réels (Neusta) | **99,05 %** | ≥ 95 % ✅ |

---

## Structure du projet

```
BioSense360/
├── Data/          — Données brutes (Météo France + Neusta)
├── notebooks/     — Notebook d'analyse
├── production/    — API REST et déploiement
└── dashboard/     — Tableau de bord interactif
```

---

## Prérequis

```bash
pip install pandas numpy scikit-learn matplotlib seaborn jupyter joblib
```

## Exécution

```bash
jupyter notebook notebooks/BioSense360_Pipeline_IA_v3.ipynb
```

---

## Références

- Masterton & Richardson (1979). *Humidex.* Environment Canada.
- Breiman (2001). *Random Forests.* Machine Learning, 45(1).
- OHCOW (2022). *Heat Stress Humidex-Based Guideline.*
- NIOSH (2016). *Occupational Exposure to Heat.*
