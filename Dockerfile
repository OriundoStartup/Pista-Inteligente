# Usar una imagen base oficial de Python
# Usamos slim para que sea ligera
FROM python:3.9-slim

# Variables de entorno para optimización
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1
ENV PYTHONPATH=/app

# Establecer el directorio de trabajo en el contenedor
WORKDIR /app

# Copiar el archivo de requerimientos primero para aprovechar la cache de Docker
COPY requirements.txt .

# Instalar las dependencias
RUN pip install --no-cache-dir -r requirements.txt

# Copiar el resto del código de la aplicación
COPY . .

# Exponer el puerto que usa Cloud Run (8080 por defecto)
EXPOSE 8080

# Configuración de Gunicorn optimizada para Cloud Run:
# --workers 2: Usar 2 workers para mejor concurrency
# --threads 4: 4 threads por worker para I/O bound tasks
# --timeout 0: Desactivar timeout (Cloud Run maneja esto)
# --preload: Precargar la app para compartir memoria entre workers
# --keep-alive 5: Mantener conexiones activas
CMD ["gunicorn", "--bind", "0.0.0.0:8080", "--workers", "2", "--threads", "4", "--timeout", "0", "--keep-alive", "5", "app:app"]
