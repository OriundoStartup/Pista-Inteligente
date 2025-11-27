# Usar una imagen base de Python 3.10 oficial (versión slim para menor tamaño)
FROM python:3.10-slim

# Establecer el directorio de trabajo en el contenedor
WORKDIR /app

# Copiar el archivo de requerimientos primero para aprovechar la caché de Docker
COPY requirements.txt .

# Instalar las dependencias
RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt

# Copiar el resto del código del proyecto al contenedor
COPY . .

# Exponer el puerto 7860 (Estándar para Hugging Face Spaces)
EXPOSE 7860

# Comando para ejecutar la aplicación Streamlit usando el módulo de python
CMD ["python", "-m", "streamlit", "run", "app_frontend.py", "--server.port", "7860", "--server.address", "0.0.0.0"]
