# --- Etapa de construcción de Frontend (Tailwind CSS) ---
FROM node:20-alpine AS frontend_build_stage

# Establece el directorio de trabajo
WORKDIR /app/frontend

# Copia los archivos necesarios para la compilación de Tailwind
# package.json es para instalar tailwindcss y sus dependencias
COPY package.json ./
COPY tailwind.config.js ./
COPY static/css/input.css static/css/input.css

# Instala las dependencias de Node.js (incluyendo tailwindcss)
RUN npm install

# Compila el CSS de Tailwind
# Asegúrate de que la ruta de salida sea donde Flask espera el archivo (static/css/)
RUN npx tailwindcss -i ./static/css/input.css -o ./static/css/output.css --minify

# --- Etapa de ejecución de la aplicación Flask ---
FROM python:3.10-slim AS app_run_stage

# Establece el directorio de trabajo para la aplicación Flask
WORKDIR /app

# Copia los requirements de Python
COPY requirements.txt .

# Instala las dependencias de Python
RUN pip install --no-cache-dir -r requirements.txt

# Copia todos los archivos de la aplicación Flask
COPY . /app

# Copia el CSS compilado de la etapa de construcción a la ubicación final esperada por Flask
# La ruta de origen es relativa al WORKDIR de frontend_build_stage
# La ruta de destino es relativa al WORKDIR de app_run_stage
COPY --from=frontend_build_stage /app/frontend/static/css/output.css /app/static/css/output.css

# AQUI DEBES AGREGAR LA LINEA PARA COPIAR init_db.py
COPY init_db.py /app/init_db.py

# Copia el script de entrada
COPY entrypoint.sh /usr/local/bin/entrypoint.sh
RUN chmod +x /usr/local/bin/entrypoint.sh

# Expone el puerto en el que Flask se ejecutará
EXPOSE 5000

# Usa el script de entrada para preparar y ejecutar la aplicación
ENTRYPOINT ["/usr/local/bin/entrypoint.sh"]

# Comando por defecto para el entrypoint
CMD ["flask", "run", "--host=0.0.0.0"]