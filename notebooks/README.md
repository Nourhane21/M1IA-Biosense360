# BioSense360 — Notebook d'Analyse

> **TER Master 1 IA — Université de Toulouse**
> **Client :** Neusta (Damien Appert)
> **Équipe :** Nourhane Mallek · Soufiane Khallouki · Daniil Zhdanov

---

## Présentation

Le notebook `BioSense360_Pipeline_IA_v3.ipynb` couvre l'intégralité du pipeline IA,
de l'acquisition des données jusqu'à l'évaluation des modèles de prédiction du confort thermique.

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

Entraînement et évaluation comparative de trois modèles de classification supervisée :

| Cellule | Contenu |
|---------|---------|
| 2.1 | Calcul de l'indice Humidex et attribution des classes (0–7) |
| 2.2 | Entraînement des modèles (Random Forest, Gradient Boosting, Régression Logistique) |
| 2.3 | Évaluation : accuracy, matrice de confusion, rapport de classification |
| 2.4 | Validation croisée 5-fold |

**Résultats :**

| Modèle | Accuracy (test 20 %) |
|--------|---------------------|
| Random Forest (500 arbres, Entropie) | **99,98 %** |
| Gradient Boosting | 99,74 % |
| Régression Logistique | 97,22 % |

Validation croisée 5-fold (Random Forest) : **99,96 % ± 0,04 %**

Le modèle Random Forest est retenu. Le modèle sérialisé est disponible dans `production/models/`.

> ⚠️ Le fichier modèle `modele_rf.pkl` n'est pas versionné (> 100 MB). À générer en exécutant le notebook.

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
