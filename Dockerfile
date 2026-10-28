FROM python:3.10-slim

# Instalar dependencias del sistema operativo (LilyPond, Timidity y FFmpeg)
RUN apt-get update && apt-get install -y \
    lilypond \
    timidity \
    ffmpeg \
    && rm -rf /var/lib/apt/lists/*

# Establecer el directorio de trabajo
WORKDIR /app

# Instalar dependencias de Python
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copiar todo el código del proyecto al contenedor
COPY . .

# Exponer el puerto de Flask
EXPOSE 5000

# Comando para iniciar la aplicación adaptada al puerto de la nube
CMD ["python", "app.py"]