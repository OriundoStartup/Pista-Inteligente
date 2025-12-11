# Usar una imagen base oficial de Python
# Usamos slim para que sea ligera
FROM python:3.9-slim

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

# Comando para ejecutar la aplicación con Gunicorn (servidor de producción)
# "app:app" significa: archivo app.py, variable app
CMD ["gunicorn", "--bind", "0.0.0.0:8080", "app:app"]
