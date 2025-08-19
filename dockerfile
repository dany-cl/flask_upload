# Image de base Python
FROM python:3.13-slim

# Définir le répertoire de travail
WORKDIR /app

# Copier uniquement requirements.txt pour installer les dépendances
COPY requirements.txt .

# Installer les dépendances
RUN pip install --no-cache-dir -r requirements.txt

# Copier le reste de l'application
COPY . .

# Exposer le port de Flask
EXPOSE 5000

# Lancer l’application
CMD ["python", "my_app.py"]
