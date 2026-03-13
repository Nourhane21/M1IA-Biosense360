# Tests — BioSense360 Production

> **TER Master 1 IA — Université de Toulouse**
> Outil : **pytest 8.4** | Couverture : **pytest-cov**
> Dernière exécution : **66 / 66 PASSED — 78 % de couverture**

---

## Résultats d'exécution

```
============================= test session starts =============================
platform win32 -- Python 3.11.9
collected 66 items

tests/test_api.py        18 passed
tests/test_humidex.py    31 passed
tests/test_predictor.py  17 passed
=============================== 66 passed in 1.65s ============================
```

### Couverture par module

| Module | Lignes | Non couvertes | Couverture | Note |
|--------|--------|---------------|------------|------|
| `biosense360/__init__.py` | 5 | 0 | **100 %** | — |
| `biosense360/config.py` | 22 | 0 | **100 %** | Constantes + SYSTEME_ALARME |
| `biosense360/humidex.py` | 16 | 0 | **100 %** | Calcul + classification |
| `biosense360/api/__init__.py` | 2 | 0 | **100 %** | — |
| `biosense360/predictor.py` | 54 | 3 | **94 %** | Chemin `.from_file()` réel (pkl) |
| `biosense360/api/app.py` | 55 | 19 | **65 %** | `create_app()` direct + bloc `__main__` |
| `biosense360/api/__main__.py` | 15 | 15 | **0 %** | Point d'entrée CLI — non testé par design |
| **TOTAL** | **169** | **37** | **78 %** | — |

> Les lignes non couvertes sont toutes des **points d'entrée CLI** ou des **branches
> de démarrage direct** (`if __name__ == '__main__'`), qui requièrent une exécution
> réelle du processus — pas des tests unitaires. Le code métier (calcul, prédiction,
> routes API) est couvert à 94–100 %.

---

## Structure des tests

```
production/tests/
├── conftest.py          Fixtures partagées (modèle simulé, client Flask)
├── test_humidex.py      31 tests — calcul Humidex + classification (0–7)
├── test_predictor.py    17 tests — moteur de prédiction BioSensePredictor
└── test_api.py          18 tests — endpoints REST /health /predict /seuils
```

---

## Lancer les tests

### Basique
```bash
cd production
pytest tests/ -v
```

### Avec rapport de couverture (terminal)
```bash
pytest tests/ -v --cov=biosense360 --cov-report=term-missing
```

### Avec rapport HTML (navigateur)
```bash
pytest tests/ --cov=biosense360 --cov-report=html
# Ouvrir production/htmlcov/index.html
```

### Un seul module
```bash
pytest tests/test_humidex.py -v
pytest tests/test_api.py -v
pytest tests/test_predictor.py -v
```

### Filtrer par nom de test
```bash
pytest tests/ -k "humidex"          # tous les tests contenant "humidex"
pytest tests/ -k "hors_plage"       # tests de validation des entrées
pytest tests/ -k "not limite"       # exclure les tests aux limites
```

---

## Description détaillée des suites

---

### `test_humidex.py` — 31 tests

Valide les deux fonctions du module `biosense360/humidex.py`.

#### `TestCalculerHumidex` (13 tests)

| Test | Ce qui est vérifié |
|------|--------------------|
| `test_conditions_normales` | À 20 °C / 30 % HR : HX ∈ ]18, 25[ |
| `test_valeur_connue` | À 30 °C / 60 % HR : HX ≈ 38.29 ± 0.5 (valeur de référence) |
| `test_retour_float` | Le type de retour est `float` |
| `test_arrondi_deux_decimales` | Résultat arrondi exactement à 2 décimales |
| `test_temperature_limite_basse` | −50 °C acceptable (plage minimale) |
| `test_temperature_limite_haute` | +60 °C acceptable (plage maximale) |
| `test_humidite_zero` | HR = 0 % : HX < T (l'air sec refroidit) |
| `test_humidite_cent` | HR = 100 % : HX > T + 5 (humidité maximale chauffe) |
| `test_temperature_hors_plage_leve_valueerror` | −51, +61, +100, −100 °C → `ValueError` |
| `test_humidite_hors_plage_leve_valueerror` | −1, +101, +200 % → `ValueError` |

#### `TestClasseDepuisHumidex` (18 tests)

Vérifie la correspondance exacte Humidex → classe pour chaque seuil critique
(valeurs juste en-dessous et juste au seuil) :

| Humidex testé | Classe attendue | Niveau |
|---------------|-----------------|--------|
| 10.0 et 24.9 | 0 | Conditions Normales |
| 25.0 et 29.9 | 1 | Gêne légère |
| 30.0 et 33.9 | 2 | Vigilance |
| 34.0 et 37.9 | 3 | Inconfort évident |
| 38.0 et 39.9 | 4 | Alerte |
| 40.0 et 42.9 | 5 | Inconfort intense |
| 43.0 et 44.9 | 6 | Urgence Vitale |
| 45.0 et 60.0 | 7 | Danger Extrême |

Ces 16 cas paramétrés couvrent **tous les seuils de frontière** du système d'alarme,
garantissant qu'aucun décalage d'arrondi ne provoque un mauvais classement.

---

### `test_predictor.py` — 17 tests

Valide `BioSensePredictor` et `PredictionResult` dans `biosense360/predictor.py`.

> **Stratégie** : le modèle `.pkl` réel n'est pas requis. Un `MagicMock` défini dans
> `conftest.py` simule le comportement du Random Forest en retournant la classe
> attendue selon la température, ce qui permet de tester la **logique applicative**
> indépendamment du modèle.

#### `TestBioSensePredictorPredict` (15 tests)

| Test | Ce qui est vérifié |
|------|--------------------|
| `test_retourne_prediction_result` | `predict()` retourne bien un `PredictionResult` |
| `test_classe_valide` | Classe prédite ∈ [0, 7] |
| `test_humidex_coherent` | À 30 °C / 60 % HR : HX retourné > 30 |
| `test_champs_presents` | Tous les champs du dataclass sont non-vides et typés correctement |
| `test_to_dict_json_compatible` | `to_dict()` produit un dict sérialisable en JSON sans erreur |
| `test_temperature_invalide_leve_valueerror` | −51 °C et +61 °C → `ValueError` |
| `test_humidite_invalide_leve_valueerror` | −1 % et +101 % → `ValueError` |
| `test_valeurs_limites_valides` | −50/0, 60/100, 0/50, 36.6/70 → pas d'exception |

#### `TestBioSensePredictorFromFile` (2 tests)

| Test | Ce qui est vérifié |
|------|--------------------|
| `test_fichier_introuvable_leve_filenotfounderror` | Chemin inexistant → `FileNotFoundError` avec message "Modèle introuvable" |
| `test_model_info_retourne_dict` | `model_info` retourne un dict avec les clés `type`, `n_estimators`, `features`, `n_classes` |

---

### `test_api.py` — 18 tests

Valide les 3 endpoints REST de `biosense360/api/app.py` via le client Flask de test
(aucun serveur HTTP démarré, aucun port réseau utilisé).

> **Stratégie** : l'application Flask est instanciée directement avec le `BioSensePredictor`
> simulé injecté via `app.config["PREDICTOR"]`. Cela isole complètement les tests API
> de la dépendance au fichier `.pkl`.

#### `TestHealthEndpoint` — GET /health (3 tests)

| Test | Ce qui est vérifié |
|------|--------------------|
| `test_retourne_200` | Code HTTP 200 |
| `test_status_ok` | `{"status": "ok"}` dans la réponse |
| `test_champs_modele_presents` | Clés `modele` et `n_estimators` présentes |

#### `TestPredictEndpoint` — POST /predict (11 tests)

**Cas nominaux (5 tests) :**

| Test | Entrée | Attendu |
|------|--------|---------|
| `test_retourne_200_avec_entrees_valides` | `{T:22, HR:55}` | HTTP 200 |
| `test_structure_reponse` | `{T:22, HR:55}` | Tous les champs présents : `timestamp`, `entree`, `humidex`, `classe`, `niveau`, `conseil`, `protocole` |
| `test_humidex_est_float` | `{T:30, HR:60}` | `humidex` est un `float` |
| `test_classe_dans_plage` | `{T:35, HR:70}` | `classe` ∈ [0, 7] |
| `test_entree_reflectee` | `{T:28.5, HR:62}` | L'entrée est bien reflétée dans `entree` |

**Cas d'erreur (6 tests) :**

| Test | Entrée | Code HTTP attendu | Raison |
|------|--------|-------------------|--------|
| `test_corps_vide_retourne_400` | Corps vide | **400** | JSON manquant |
| `test_champ_temperature_manquant_retourne_400` | `{HR:50}` | **400** | Champ requis absent |
| `test_champ_humidite_manquant_retourne_400` | `{T:25}` | **400** | Champ requis absent |
| `test_type_invalide_retourne_400` | `{T:"chaud", HR:50}` | **400** | Type non numérique |
| `test_temperature_hors_plage_retourne_422` | `{T:100, HR:50}` | **422** | Valeur hors plage physique |
| `test_humidite_hors_plage_retourne_422` | `{T:25, HR:200}` | **422** | Valeur hors plage physique |

> La distinction **400** (requête malformée) vs **422** (donnée physiquement invalide)
> suit la sémantique HTTP stricte : 400 = problème de format, 422 = problème de valeur.

#### `TestSeuilsEndpoint` — GET /seuils (4 tests)

| Test | Ce qui est vérifié |
|------|--------------------|
| `test_retourne_200` | Code HTTP 200 |
| `test_huit_classes` | Exactement 8 entrées dans le dictionnaire |
| `test_toutes_les_classes_presentes` | Clés "0" à "7" toutes présentes |
| `test_structure_classe` | Chaque classe contient `seuil`, `niveau`, `conseil`, `protocole` (list) |

---

## Fixtures partagées (`conftest.py`)

| Fixture | Scope | Description |
|---------|-------|-------------|
| `mock_model` | session | `MagicMock` simulant un `RandomForestClassifier` — retourne la classe correcte selon T (0 si T < 25, 7 si T ≥ 45, etc.) sans charger de fichier |
| `predictor` | session | `BioSensePredictor` instancié avec `mock_model` |
| `flask_client` | session | Client Flask de test avec `predictor` injecté — aucun port réseau |

L'utilisation du scope `session` garantit que le modèle simulé n'est créé **qu'une seule fois**
pour toute la suite de tests, optimisant la vitesse d'exécution.

---

## Interprétation de la couverture

Les 37 lignes non couvertes sont toutes **attendues et justifiées** :

| Fichier | Lignes | Raison |
|---------|--------|--------|
| `api/__main__.py` (3–23) | 15 | Bloc de démarrage CLI — ne peut pas être testé sans démarrer un vrai processus |
| `api/app.py` (56–73) | 18 | Chemin `create_app()` avec chargement `.pkl` réel — remplacé par injection directe dans les tests |
| `api/app.py` (177–193) | — | Bloc `if __name__ == '__main__'` |
| `predictor.py` (146–148) | 3 | Chemin succès de `from_file()` avec vrai `.pkl` — seul le chemin d'erreur est testé unitairement |

> Pour atteindre 100 % de couverture, il faudrait ajouter des **tests d'intégration**
> démarrant un vrai serveur Flask et chargeant le fichier `modele_rf.pkl` réel.
> Ces tests sont intentionnellement séparés des tests unitaires car ils dépendent
> d'une ressource externe (le modèle entraîné).

---

## Commandes utiles

```bash
# Exécution rapide (sans couverture)
pytest tests/ -q

# Arrêt au premier échec
pytest tests/ -x

# Ré-exécuter uniquement les tests échoués
pytest tests/ --lf

# Voir la sortie print() des tests
pytest tests/ -s

# Générer un rapport JUnit (CI/CD)
pytest tests/ --junitxml=test-results.xml
```
