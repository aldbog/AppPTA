@echo off
echo =============================
echo   Initializare aplicatie Flask
echo =============================

:: Verifică dacă venv există
if not exist "venv\" (
    echo [INFO] Creare mediu virtual...
    python -m venv venv
)

:: Activează mediul virtual
echo [INFO] Activare mediu virtual...
call venv\Scripts\activate

:: Instalează dependințele
echo [INFO] Instalare dependințe din requirements.txt...
pip install -r requirements.txt

:: Rulează aplicația Flask
echo [INFO] Pornire aplicatie...
python app.py

pause
