# Videoflix Backend

Programmiert mit Django und der Möglichkeit:

- Accounts zu erstellen und per Email verifizieren zu lassen
- Namens- oder Emailanpassung im Interface
- Videos, welche vom Admin hinauf geladen worden sind, anzuschauen
- In verschiedene Formate zu konvertieren


## Installation

Anleitung zum installieren des Projekts:

- git clone https://github.com/WalterDoni/Videoflix-Backend.git
- python -m venv env
- .env/bin/activate 
- im Ordner Videoflix-Backend/videoflix_backend/videoflix_backend/env.txt befindet sich diese env.txt Datei. Zuerst muss diese auf .env geändert werden und die Variablen müssen die zugehörigen Werte bekommen.
- pip install -r requirements
- python manage.py createsuperuser
- python manage.py runserver
- Öffne den locahost und logge dich mit deinen superuser ein

# Deployment

Um das Programm auf einem Server zu hosten würde ich Nginx , Gunicorn und Supervisor empfehlen. 
