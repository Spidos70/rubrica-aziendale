FROM python:3.12-slim

WORKDIR /app

# Installa dipendenze Python
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copia sorgenti
COPY . .

# Cartella dati (volume mount point)
RUN mkdir -p /app/data

EXPOSE 5000

# Avvia con Gunicorn (2 worker, abbastanza per uso interno)
CMD ["gunicorn", "--bind", "0.0.0.0:5000", "--workers", "2", "--timeout", "60", "app:app"]
