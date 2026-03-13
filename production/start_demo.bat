@echo off
chcp 65001 >nul
title BioSense360 — Demo

echo.
echo  ╔══════════════════════════════════════════════════════╗
echo  ║         BioSense360 — Demonstration                 ║
echo  ╚══════════════════════════════════════════════════════╝
echo.

cd /d "%~dp0"

python --version >nul 2>&1
if errorlevel 1 (
    echo  [ERREUR] Python n'est pas installe.
    pause & exit /b 1
)

if not exist "models\modele_rf.pkl" (
    echo  [ERREUR] Modele introuvable : models\modele_rf.pkl
    pause & exit /b 1
)

pip install -r requirements.txt -q

echo  Lancement de la demonstration...
echo.
python demo.py

pause
