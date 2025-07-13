# Usa una imagen base que tenga Node.js y Python
FROM node:20-alpine AS build_stage

# Instala Python y pip (necesario para esta imagen base específica)
RUN apk add --no-cache python3 py3-pip

# Establece el directorio de trabajo para la fase de construcción de Frontend (Tailwind)
WORKDIR /app/frontend

# Copia SOLO el package.json primero
COPY package.json ./

# Instala las dependencias de Node.js, lo que CREARÁ package-lock.json dentro del contenedor
RUN npm install

# Ahora que package-lock.json existe (dentro del contenedor), puedes copiar otros archivos si es necesario
# (aunque para este caso, ya no es estrictamente necesario copiarlo si se generó aquí)

# Copia los archivos de Tailwind (input.css y config)
COPY tailwind.config.js ./
COPY ./static/css/input.css ./static/css/input.css

# Compila el CSS de Tailwind
RUN npx tailwindcss -i ./static/css/input.css -o ./static/css/output.css --minify

# --- Etapa de ejecución de la aplicación Flask (más ligera) ---
FROM python:3.10-slim AS run_stage

# Establece el directorio de trabajo para la aplicación Flask
WORKDIR /app

# Copia los requirements de Python
COPY requirements.txt .

# Instala las dependencias de Python
RUN pip install --no-cache-dir -r requirements.txt

# Copia los archivos de la aplicación Flask y el CSS compilado
COPY . /app

# Mueve el CSS compilado de la etapa de build a la etapa de ejecución
COPY --from=build_stage /app/frontend/static/css/output.css /app/static/css/output.css

# Expone el puerto en el que Flask se ejecutará.
EXPOSE 5000

# Comando para ejecutar la aplicación Flask.
CMD ["flask", "run", "--host=0.0.0.0"]