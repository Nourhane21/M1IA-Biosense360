# BioSense — Environmental Viability & Habitability Prediction

BioSense est un prototype qui exploite des **capteurs environnementaux** pour collecter en continu des données (température, humidité, qualité de l’air, etc.) ainsi que des **indices de confort thermique**.  
L’objectif est de transformer ces mesures brutes en **informations directement exploitables** afin d’évaluer si un lieu est **favorable** ou **à risque** pour :
- la **santé humaine** (confort / exposition)
- la **santé des plantes** (conditions de croissance / stress)

---

## 1) Contexte & objectifs

Les mesures brutes fournies par les capteurs sont souvent difficiles à interpréter directement. BioSense vise à :
- **nettoyer** et **structurer** les données capteurs (qualité, unité, fréquence)
- **calculer des indicateurs** (indices de confort, scores de qualité, agrégations temporelles)
- **détecter des situations à risque** (seuils, alertes, dérives)
- produire un **score d’habitabilité** et une **interprétation** (favorable / vigilance / risque)

---

## 2) Fonctionnalités (cibles)

- **Ingestion** des données capteurs (stream ou batch)
- **Pré-traitement** : nettoyage, gestion des valeurs manquantes, harmonisation des unités
- **Feature engineering** : indices thermiques, agrégats (min/max/moyennes glissantes), tendances
- **Évaluation habitabilité** :
  - score **Humain**
  - score **Plante**
  - statut global : `Favorable` / `À surveiller` / `Risque`
- **Restitution** : dashboard, API, export (CSV/JSON), alertes (si activées)

> Remarque : la liste exacte dépend des capteurs disponibles et du périmètre du client.

---

## 3) Architecture (vue simplifiée)

1. **Capteurs** → mesures brutes (température, humidité, air, etc.)
2. **Pipeline data** :
   - ingestion → nettoyage → normalisation → calcul d’indices → scoring
3. **Sorties** :
   - indicateurs + scores + statut + recommandations

---

## 4) Données & indicateurs

### Capteurs 
- Température (°C)
- Humidité relative (%)
- Qualité de l’air (PM2.5 / CO₂ / TVOC selon capteurs)
- Autres si disponibles : luminosité, vent, pression, etc.

### Indices 
- Indices de confort thermique (ex. humidex / heat index selon choix projet)
- Agrégations temporelles (moyenne glissante 10 min, max sur 1h, etc.)
- Score de risque basé sur seuils (règles) ou modèle (ML)

---




