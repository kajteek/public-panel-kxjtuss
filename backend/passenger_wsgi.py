import sys
import os

# Dodaje obecny katalog do ścieżki Pythona
cwd = os.getcwd()
sys.path.append(cwd)

# Importuje 'app' z pliku app.py i udostępnia jako 'application' dla serwera Plesk
from app import app as application
