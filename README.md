# LSPD Document Generator API & Web App

Aplikacja sieciowa do generowania oficjalnych dokumentów San Andreas Police Department (LSPD) w formacie PDF i PNG. Projekt zawiera własny dedykowany backend w Python (Flask) oraz nowoczesny frontend napisany w plain HTML, CSS (Glassmorphism) i JavaScript.

## 🚀 Jak uruchomić to lokalnie

1. Upewnij się, że masz Pythona 3.10+
2. Zainstaluj biblioteki: `pip install -r backend/requirements.txt`
3. Wejdź do folderu `backend`: `cd backend`
4. Odpal serwer HTTP: `python app.py` 
5. Strona automatycznie serwuje samą siebie, więc wejdź po prostu na adres: `http://localhost:5000/`

## 🌍 Jak przygotować to pod Hosting (np. Render, Heroku)

Aplikacja jest już w 100% gotowa na produkcję! Skonfigurowałem ją w sposób absolutnie minimalizujący twój narzut pracy:
- W `app.py` znajduje się system podający zawartość katalogu `frontend` wprost z hostingu backendu.
- Strona korzysta wyłącznie ze ścieżki `/api/generate` podczas tworzenia PDF, więc niezależnie na jakiej domenie to wepniesz - zadziała natychmiast, bez zmieniania ustawień adresów.

Podczas definiowania projektu na GitHubie, a potem na wybranym hostingu:
1. Skopiuj ten cały utworzony folder (obydwa foldery `backend/` oraz `frontend/` i ten plik `README.md`) na GitHuba jako nowe repozytorium.
2. Po podłączeniu na hosting typu Render, w sekcji "Root Directory" wpisz `backend` albo podaj mu, że pliki uruchomieniowe leżą w `backend`. Wtedy poleceniem startowym musi być: `gunicorn app:app`.
3. Gotowe. Ciesz się stroną!

## Informacje niezbędne do Hostingu

Wszystko zostało skonfigurowane tak, aby ruszyło z "pierwszego strzała". Upewnij się tylko na docelowym hostingu o tych krokach:
* **Command Build:** `pip install -r requirements.txt` (gdy hostujesz z foldera `backend)
* **Command Start:** `gunicorn app:app` (Zamiast `python app.py`) - Wymagane przez większość platform pod czysty ruch HTTP. Pakiet `gunicorn` jest już dopisany do `requirements.txt`.
* **Environment Variables:** Nie wymagasz żadnych zmiennych `.env` aby API LSPD działało!
* **Port:** Domyślnie na lokalnej maszynie jest to 5000, jednak Hostingi wymuszaja swoje. Zostaw to ich domyślnej konfiguracji, `Flask` i `gunicorn` ogarną to same.

---

Obydwie funkcjonalności (logotypy obok siebie, oraz załączanie wielu zdjęć i podgląd) zostały w pełni wdrożone bez ingerencji w Twój proces wrzucania na produkcję!
