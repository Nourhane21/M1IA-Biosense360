"""
BioSense360 — Préparation des données pour le dashboard
=======================================================
Génère dashboard_data.json à partir de :
  - Météo France Toulouse-Blagnac (extérieur, classes 0–6)
  - Neusta ClimaTrack (intérieur, classes 0–1)

Usage :
    cd dashboard
    python prepare_dashboard_data.py
"""
import json
import os
import sys
import glob
from datetime import datetime
from collections import defaultdict

sys.stdout.reconfigure(encoding="utf-8")

import pandas as pd

# ── Chemins ───────────────────────────────────────────────────────────────────
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
METEO_CSV   = os.path.join(ROOT, "data", "meteo_France_data", "data202425.csv")
NEUSTA_DIR  = os.path.join(ROOT, "data", "Neusta",
              "Data-Climatrack-MKII-20260323T090240Z-3-001",
              "Data-Climatrack-MKII")
OUT_FILE    = os.path.join(os.path.dirname(os.path.abspath(__file__)), "dashboard_data.json")

# ── Formules métier ──────────────────────────────────────────────────────────
SEUILS   = [25, 30, 34, 38, 40, 43, 45]
NIVEAUX  = ["Conditions Normales","Gêne légère","Vigilance","Inconfort évident",
            "Alerte","Inconfort intense","Urgence Vitale","Danger Extrême"]
COLORS   = ["#22c55e","#a3e635","#facc15","#fb923c",
            "#f87171","#ef4444","#dc2626","#991b1b"]

def humidex(T: float, HR: float) -> float:
    e = 6.112 * (10 ** (7.5 * T / (237.7 + T))) * (HR / 100)
    return round(T + (5 / 9) * (e - 10), 2)

def classe(hx: float) -> int:
    for i, s in enumerate(SEUILS):
        if hx < s:
            return i
    return 7

# ─────────────────────────────────────────────────────────────────────────────
# 1. MÉTÉO FRANCE — Toulouse-Blagnac
# ─────────────────────────────────────────────────────────────────────────────
print("Chargement Météo France …", end=" ", flush=True)
df = pd.read_csv(METEO_CSV, sep=";", usecols=["validity_time", "t", "u", "name"],
                 low_memory=False)
df = df[df["name"].str.contains("TOULOUSE|BLAGNAC", case=False, na=False)].copy()
df["t_c"] = df["t"] - 273.15
df = df.dropna(subset=["t_c", "u"])
df["dt"]   = pd.to_datetime(df["validity_time"])
df["date"] = df["dt"].dt.strftime("%Y-%m-%d")
df["heure"] = df["dt"].dt.hour
df["hx"]   = df.apply(lambda r: humidex(r["t_c"], r["u"]), axis=1)
df["cls"]  = df["hx"].apply(classe)
print(f"{len(df)} observations — {df['date'].nunique()} jours")

# Agréger par jour + heure (déjà 1 obs toutes les 3h, pas besoin de groupby)
meteo_days = {}
for date, grp in df.groupby("date"):
    rows = []
    for _, row in grp.sort_values("heure").iterrows():
        rows.append({
            "h":   int(row["heure"]),
            "T":   round(float(row["t_c"]), 1),
            "HR":  round(float(row["u"]), 1),
            "HX":  round(float(row["hx"]), 2),
            "cls": int(row["cls"]),
        })
    max_cls  = max(r["cls"] for r in rows)
    max_hx   = max(r["HX"] for r in rows)
    t_vals   = [r["T"] for r in rows]
    hr_vals  = [r["HR"] for r in rows]
    meteo_days[date] = {
        "date": date,
        "source": "Météo France — Toulouse-Blagnac (extérieur)",
        "obs": rows,
        "stats": {
            "max_cls": max_cls,
            "max_hx":  round(max_hx, 2),
            "min_T":   round(min(t_vals), 1),
            "max_T":   round(max(t_vals), 1),
            "avg_HR":  round(sum(hr_vals) / len(hr_vals), 1),
            "n_cls":   {str(c): sum(1 for r in rows if r["cls"] == c) for c in range(8)},
        },
    }

print(f"  → {len(meteo_days)} jours Météo France traités")

# ─────────────────────────────────────────────────────────────────────────────
# 2. NEUSTA — agrégation horaire (moyenne par heure)
# ─────────────────────────────────────────────────────────────────────────────
print("Chargement Neusta …", end=" ", flush=True)
neusta_days = {}
json_files  = sorted(glob.glob(os.path.join(NEUSTA_DIR, "*.json")))

def load_neusta_records(fpath):
    """Charge un fichier Neusta : JSON array OU NDJSON (une ligne par objet)."""
    with open(fpath, encoding="utf-8") as f:
        content = f.read().strip()
    try:
        data = json.loads(content)
        return data if isinstance(data, list) else [data]
    except json.JSONDecodeError:
        # NDJSON : une ligne = un objet JSON
        records = []
        for line in content.splitlines():
            line = line.strip()
            if line:
                try:
                    records.append(json.loads(line))
                except Exception:
                    pass
        return records

for fpath in json_files:
    date_str = os.path.basename(fpath).replace("merged_data_", "").replace(".json", "")
    try:
        raw = load_neusta_records(fpath)
    except Exception:
        continue

    # Agréger par heure
    by_hour = defaultdict(list)
    for rec in raw:
        try:
            ts = rec.get("timestamp", "")
            # Champs : "Temperature"/"Humidity" (ancien) ou "temperature"/"humidity" (nouveau)
            T  = float(rec.get("Temperature", rec.get("temperature", None)))
            HR = float(rec.get("Humidity",    rec.get("humidity",    None)))
            if T is None or HR is None:
                continue
            # Format timestamp : "DD-MM-YYYY HH:MM:SS"
            h = int(ts.split(" ")[1].split(":")[0]) if " " in ts else 0
            by_hour[h].append((T, HR))
        except Exception:
            continue

    rows = []
    for h in sorted(by_hour):
        vals = by_hour[h]
        T_avg  = sum(v[0] for v in vals) / len(vals)
        HR_avg = sum(v[1] for v in vals) / len(vals)
        hx     = humidex(T_avg, HR_avg)
        rows.append({
            "h":   h,
            "T":   round(T_avg, 1),
            "HR":  round(HR_avg, 1),
            "HX":  round(hx, 2),
            "cls": classe(hx),
        })

    if not rows:
        continue

    max_cls = max(r["cls"] for r in rows)
    max_hx  = max(r["HX"] for r in rows)
    t_vals  = [r["T"] for r in rows]
    hr_vals = [r["HR"] for r in rows]

    neusta_days[date_str] = {
        "date":   date_str,
        "source": "Neusta ClimaTrack (intérieur)",
        "obs":    rows,
        "stats": {
            "max_cls": max_cls,
            "max_hx":  round(max_hx, 2),
            "min_T":   round(min(t_vals), 1),
            "max_T":   round(max(t_vals), 1),
            "avg_HR":  round(sum(hr_vals) / len(hr_vals), 1),
            "n_cls":   {str(c): sum(1 for r in rows if r["cls"] == c) for c in range(8)},
        },
    }

print(f"{len(neusta_days)} jours Neusta traités")

# ─────────────────────────────────────────────────────────────────────────────
# 3. Calendrier de synthèse (pour la heatmap)
# ─────────────────────────────────────────────────────────────────────────────
calendar_meteo  = [
    {"date": d, "max_cls": v["stats"]["max_cls"], "max_hx": v["stats"]["max_hx"],
     "max_T": v["stats"]["max_T"]}
    for d, v in sorted(meteo_days.items())
]
calendar_neusta = [
    {"date": d, "max_cls": v["stats"]["max_cls"], "max_hx": v["stats"]["max_hx"],
     "max_T": v["stats"]["max_T"]}
    for d, v in sorted(neusta_days.items())
]

# ─────────────────────────────────────────────────────────────────────────────
# 4. Export JSON
# ─────────────────────────────────────────────────────────────────────────────
out = {
    "metadata": {
        "generated":      datetime.now().isoformat(),
        "model":          "RandomForestClassifier — 500 arbres — Entropie",
        "accuracy_test":  99.98,
        "accuracy_neusta": 99.05,
        "sources": {
            "meteo":  f"Météo France Toulouse-Blagnac — {len(meteo_days)} jours",
            "neusta": f"Neusta ClimaTrack — {len(neusta_days)} jours",
        },
    },
    "niveaux": [
        {"cls": i, "niveau": NIVEAUX[i], "color": COLORS[i],
         "seuil": ["HX<25","25≤HX<30","30≤HX<34","34≤HX<38",
                   "38≤HX<40","40≤HX<43","43≤HX<45","HX≥45"][i]}
        for i in range(8)
    ],
    "meteo_days":       meteo_days,
    "neusta_days":      neusta_days,
    "calendar_meteo":   calendar_meteo,
    "calendar_neusta":  calendar_neusta,
}

with open(OUT_FILE, "w", encoding="utf-8") as f:
    json.dump(out, f, ensure_ascii=False, separators=(",", ":"))

# Générer aussi dashboard_data.js (compatible file:// sans serveur HTTP)
JS_FILE = os.path.join(os.path.dirname(os.path.abspath(__file__)), "dashboard_data.js")
with open(JS_FILE, "w", encoding="utf-8") as f:
    f.write("window.DASHBOARD_DATA=")
    json.dump(out, f, ensure_ascii=False, separators=(",", ":"))
    f.write(";")

size_mb = os.path.getsize(OUT_FILE) / 1_048_576
print(f"\nFichier généré : {OUT_FILE}")
print(f"Taille : {size_mb:.2f} MB")
print(f"Fichier JS : {JS_FILE}")
print(f"Clés : {list(out.keys())}")
