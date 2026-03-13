@echo off
chcp 65001 >nul
title BioSense360 — API de Vivabilite Thermique

echo.
echo  ╔══════════════════════════════════════════════════════╗
echo  ║         BioSense360 — Demarrage de l'API            ║
echo  ╚══════════════════════════════════════════════════════╝
echo.

:: Aller dans le dossier production/
cd /d "%~dp0"

:: Vérifier Python
python --version >nul 2>&1
if errorlevel 1 (
    echo  [ERREUR] Python n'est pas installe ou pas dans le PATH.
    echo  Telechargez Python sur https://www.python.org/downloads/
    pause
    exit /b 1
)

:: Vérifier que le modele existe
if not exist "models\modele_rf.pkl" (
    echo  [ERREUR] Modele introuvable : models\modele_rf.pkl
    echo  Executez d'abord le notebook pour exporter le modele.
    pause
    exit /b 1
)

:: Installer les dépendances si nécessaire
echo  Installation des dependances...
pip install -r requirements.txt -q
if errorlevel 1 (
    echo  [ERREUR] Echec de l'installation des dependances.
    pause
    exit /b 1
)
echo  Dependances OK.
echo.

:: Lancer l'API
echo  Demarrage de l'API sur http://localhost:5000
echo.
echo  Endpoints disponibles :
echo    GET  http://localhost:5000/health   (sante du service)
echo    POST http://localhost:5000/predict  (prediction)
echo    GET  http://localhost:5000/seuils   (seuils critiques)
echo.
echo  Appuyez sur Ctrl+C pour arreter le service.
echo.

python -m biosense360.api

pause
