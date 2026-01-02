FROM python:3.10-slim

# Empêche Python d'écrire des .pyc
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

WORKDIR /app

# Dépendances système minimales
RUN apt-get update && apt-get install -y \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

# Installer les dépendances Python
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copier le code
COPY . .

# Exposer le port attendu par Hugging Face
EXPOSE 7860

# Lancer l'app
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "7860"]
