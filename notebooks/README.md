# BioSense360 — Notebook d'Analyse

> **TER Master 1 IA — Université de Toulouse**
> **Client :** Neusta (Damien Appert)
> **Équipe :** Nourhane Mallek · Soufiane Khallouki · Daniil Zhdanov

---

## Présentation

Le notebook `BioSense360_Pipeline_IA_v3.ipynb` couvre l'intégralité du pipeline IA,
de l'acquisition des données jusqu'au système d'alerte thermique en temps réel.
Le tableau de bord interactif est disponible dans `dashboard/`.

---

## Partie 1 — Acquisition et Préparation des Données

| Cellule | Contenu |
|---------|---------|
| 1.1 | Chargement des jeux de données (Météo France + Neusta ClimaTrack) |
| 1.2 | Sélection et standardisation des colonnes |
| 1.3 | Nettoyage, contrôle qualité et filtrage |

**Résultats :** 461 341 observations nettoyées, 487 fichiers Neusta chargés (2 formats).

---

## Partie 2 — Modélisation et Prédiction

| Modèle | Accuracy (test 20 %) |
|--------|---------------------|
| Random Forest (500 arbres, Entropie) | **99,98 %** |
| Gradient Boosting | 99,74 % |
| Régression Logistique | 97,22 % |

Validation croisée 5-fold : **99,96 % ± 0,04 %** — Modèle retenu : Random Forest.

---

## Partie 3 — Détection des Dangers Thermiques

Système d'alerte à 8 niveaux basé sur les seuils Humidex :

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

**Validation Neusta (capteurs réels) : 99,05 % d'accuracy.**

---

## Tableau de Bord

Le tableau de bord interactif (`dashboard/dashboard.html`) permet de visualiser
les données journalières et les niveaux de confort thermique par source.

---

## Prérequis

```bash
pip install pandas numpy scikit-learn matplotlib seaborn jupyter joblib
```

## Exécution

```bash
jupyter notebook notebooks/BioSense360_Pipeline_IA_v3.ipynb
```
