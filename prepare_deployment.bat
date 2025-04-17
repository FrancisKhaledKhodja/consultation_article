@echo off
echo Préparation du déploiement...

REM Nettoyer les anciens builds
if exist "dist" rmdir /s /q "dist"
if exist "build" rmdir /s /q "build"
if exist "__pycache__" rmdir /s /q "__pycache__"

REM Créer l'exécutable avec PyInstaller
pyinstaller --onefile --noconsole --clean main.py --name consultation_article

REM Créer le dossier de déploiement s'il n'existe pas
if not exist "deployment" mkdir deployment

REM Copier l'exécutable
copy "dist\consultation_article.exe" "deployment\"

REM Copier la base de données
copy "database_sqlite\articles.db" "deployment\"

REM Créer le fichier de configuration avec le chemin relatif
echo articles.db > "deployment\database_settings.txt"

echo Déploiement terminé ! Les fichiers se trouvent dans le dossier 'deployment'
pause
