# Usa una imagen base oficial de Python 3.10.
FROM python:3.10-slim

# Actualiza el sistema e instala librerías necesarias.
RUN apt-get update && \
    apt-get install -y --no-install-recommends && \
    rm -rf /var/lib/apt/lists/*

# Establece el directorio de trabajo.
WORKDIR /app

# Copia los archivos del proyecto al contenedor.
COPY . /app

# Instala las dependencias de Python.
RUN pip install --upgrade pip
RUN pip install requests

# Comando para ejecutar el chatbot.
CMD ["python", "chatbot_pdf.py"]
