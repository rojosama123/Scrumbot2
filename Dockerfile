FROM python:3.10-slim

# Instala dependencias del sistema necesarias para PyPDF2, llama-cpp-python y scikit-learn
RUN apt-get update && \
    apt-get install -y build-essential cmake && \
    rm -rf /var/lib/apt/lists/*

# Copia los archivos del proyecto al contenedor
WORKDIR /app
COPY . /app

# Instala las dependencias de Python
RUN pip install --upgrade pip
RUN pip install -r requirements.txt

# Expone el puerto si tu bot es web (opcional)
# EXPOSE 8000

# Comando para ejecutar el chatbot
CMD ["python", "chatbot_pdf.py"]