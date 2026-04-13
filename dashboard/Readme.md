# BioSense360 : Dashboard de Vivabilité Thermique

> Surveillance en temps réel de la vivabilité thermique par indice Humidex  
> Projet M1 Intelligence Artificielle : Université de Toulouse · Client : **Neusta**

---

## Présentation

Le tableau de bord interactif de surveillance thermique est conçu pour évaluer les risques liés à la chaleur en milieu de travail. Il combine des données météorologiques extérieures (Météo France : station Toulouse-Blagnac) et des relevés intérieurs issu des capteurs Neusta ClimaTrack pour produire une classification Humidex horaire et des recommandations de sécurité conformes aux référentiels réglementaires en vigueur.

Le modèle de classification sous-jacent est un **Random Forest** (500 arbres, critère entropie) atteignant **99,98 %** de précision sur les données de test et **99,05 %** sur la validation Neusta.

---

## Fonctionnalités

### Onglet : Analyse journalière
- **Calendrier thermique annuel** : visualisation colorée jour par jour (8 niveaux de classe Humidex), navigation par année.
- **Sélection de source** : bascule entre les données Météo France (extérieur) et Neusta (intérieur).
- **Statistiques journalières** : classe maximale, Humidex max, température min/max, humidité moyenne, nombre de relevés.
- **Graphique horaire** : évolution de l'Humidex (barres colorées par classe) et de la température (courbe).
- **Répartition en donut** : distribution des classes sur la journée.
- **Protocoles de sécurité** : recommandations dynamiques par classe (OHCOW, ACGIH TLV, NIOSH, HAS, INRS, Décret 2025-482).
- **Tableau horaire détaillé** : cliquer sur une ligne pour afficher le protocole de la classe correspondante.
- **Chronologie temporelle** : graphique multi-mode (Classe / Humidex / Température) sur l'ensemble de la période.

### Onglet : Carte & Déplacement
- **Carte thermique interactive** (Leaflet + CartoDB Dark) des stations Météo France, avec marqueurs colorés par classe et infobulles détaillées.
- **Moteur de recommandation de déplacement thermique** :
  - Sélection d'une zone de départ et d'une zone d'arrivée.
  - Matrice de risque 8×8 (départ × arrivée) interactive.
  - Protocole en 4 phases : *Avant le départ · Transit · À l'arrivée · Suivi*.
  - Durée d'acclimatation estimée (NIOSH 2016).
  - Alertes légales automatiques selon le niveau d'arrivée.

---

## Structure du projet

```
dashboard/
├── dashboard.html          # Interface principale (fichier unique auto-contenu)
├── dashboard_data.js       # Données pré-calculées (généré par le script Python)
└── prepare_dashboard_data.py  # Script de préparation des données
```

---

## Installation & lancement

### Prérequis

| Dépendance | Version minimale |
|---|---|
| Python | 3.9+ |
| Navigateur moderne | Chrome 110+, Firefox 110+, Edge 110+ |
| Connexion Internet | Requise pour Leaflet et Chart.js (CDN) |

### 1. Préparer les données

```bash
python prepare_dashboard_data.py
```

Ce script génère `dashboard_data.js` dans le dossier `dashboard/`. Il lit les fichiers CSV bruts (Météo France et Neusta), calcule l'indice Humidex, applique le modèle de classification et produit les agrégats journaliers et les données par station.

### 2. Ouvrir le dashboard

```bash
# Depuis le dossier dashboard/
open dashboard.html          # macOS
xdg-open dashboard.html      # Linux
start dashboard.html         # Windows
```

> ⚠️ Ouvrez `dashboard.html` **depuis le dossier `dashboard/`** afin que `dashboard_data.js` soit correctement chargé.

---

## Modèle Humidex & Classification

### Formule Humidex (Masterton & Richardson, 1979)

```
e = 6,112 × 10^(7,5T / (237,7 + T)) × HR / 100
HX = T + 0,5555 × (e − 10)
```

Avec `T` la température en °C et `HR` l'humidité relative en %.

### Échelle de classification (8 niveaux)

| Classe | Seuil Humidex | Niveau | Couleur |
|:---:|---|---|---|
| 0 | HX < 25 | Conditions Normales | 🟢 `#22c55e` |
| 1 | 25 ≤ HX < 30 | Gêne légère | 🟡 `#a3e635` |
| 2 | 30 ≤ HX < 34 | Vigilance | 🟡 `#facc15` |
| 3 | 34 ≤ HX < 38 | Inconfort évident | 🟠 `#fb923c` |
| 4 | 38 ≤ HX < 40 | Alerte | 🔴 `#f87171` |
| 5 | 40 ≤ HX < 43 | Inconfort intense | 🔴 `#ef4444` |
| 6 | 43 ≤ HX < 45 | Urgence Vitale | 🔴 `#dc2626` |
| 7 | HX ≥ 45 | Danger Extrême | 🟥 `#991b1b` |

---

## 📄 Référentiels réglementaires & scientifiques

| Référentiel | Usage |
|---|---|
| **OHCOW 2022** | Seuils de classes thermiques et protocoles de retrait |
| **ACGIH TLV 2023** | Cycles travail/repos, limite hydrique (1,5 L/h) |
| **NIOSH DHHS-2016-106** | Hydratation (0,75 L/h), acclimatation progressive |
| **HAS 2023** | Protocole coup de chaleur, populations vulnérables |
| **INRS R-447** | Report des travaux lourds, pauses à l'ombre |
| **Décret n° 2025-482** | DUERP chaleur, obligation de local climatisé, responsabilité pénale |
| **Masterton & Richardson 1979** | Formule de calcul de l'indice Humidex |
| **Bouchama & Knochel (NEJM, 2002)** | Mortalité coup de chaleur (10–50 % sans prise en charge) |

---

## Populations vulnérables

Pour les classes ≥ 5, le protocole de la classe supérieure s'applique aux personnes suivantes (seuil de danger atteint ~5 unités Humidex plus tôt) :

- Personnes âgées (> 65 ans)
- Femmes enceintes
- Nourrissons (< 1 an)
- Acclimatation insuffisante
- Obésité (IMC ≥ 30)
- Cardiopathie / HTA
- Traitement diurétique ou anticholinergique
- Pathologie respiratoire chronique
- Effort physique intense non habituel

---

## Architecture technique

```
dashboard.html
│
├── Chart.js 4.4.0 (CDN)          → Graphiques horaires, donut, chronologie
├── Leaflet 1.9.4 (CDN)           → Carte thermique interactive
├── dashboard_data.js             → Données injectées (window.DASHBOARD_DATA)
│
└── JavaScript (inline)
    ├── ALARME{}                  → Configuration des 8 classes
    ├── initUI()                  → Initialisation calendrier + sélection date
    ├── buildCalendar()           → Rendu du calendrier thermique
    ├── showDay() / renderDay()   → Affichage d'une journée
    ├── buildTimeline()           → Graphique chronologique
    ├── initMap()                 → Carte Leaflet + marqueurs stations
    ├── computeCross()            → Moteur de recommandation déplacement
    └── getCrossSteps()           → Génération du protocole en 4 phases
```

### Format de `dashboard_data.js`

```javascript
window.DASHBOARD_DATA = {
  meteo_days:      { "YYYY-MM-DD": { obs: [...], stats: {...}, source: "..." } },
  neusta_days:     { "YYYY-MM-DD": { obs: [...], stats: {...}, source: "..." } },
  calendar_meteo:  [ { date, max_cls, max_hx }, ... ],
  calendar_neusta: [ { date, max_cls, max_hx }, ... ],
  stations_list:   [ { name, lat, lon }, ... ],
  stations_daily:  { "YYYY-MM-DD": [ [cls, hx, maxT], ... ] }
};
```

Chaque observation horaire (`obs`) contient : `h` (heure), `T` (°C), `HR` (%), `HX` (Humidex), `cls` (classe 0–7).

---

## Équipe & Encadrement

Daniil Zhdanov
Nourhane Mallek
Soufiane Khallouki
---

 

*BioSense360 v3.0 : Surveillance de Vivabilité Thermique*