# Chatbot basico
Este chatbot funciona unicamente en terminal, por ahora.

Para hacerlo funcionar deben hacer lo de abajo.


## Instalación de Microsoft C++ Build Tools


Algunas librerías de Python requieren compilar código nativo. Para ello, es necesario instalar Microsoft C++ Build Tools. Sigue estos pasos:

1. Ve a la página oficial de descarga: https://visualstudio.microsoft.com/visual-cpp-build-tools/
2. Descarga el instalador y ejecútalo.
3. En el instalador, selecciona "Herramientas de compilación de C++" (C++ build tools).
4. Haz clic en "Instalar" y espera a que finalice el proceso.
5. Una vez instalado, reinicia tu computadora si el instalador lo solicita.

Esto permitirá compilar extensiones de Python que lo requieran (por ejemplo, al instalar paquetes como `llama-cpp-python`).

## Construcción de la imagen Docker de manera local

1. Abre una terminal en la carpeta raíz del proyecto (donde está el `Dockerfile`).
2. Ejecuta el siguiente comando para construir la imagen (puedes cambiar el nombre `chatbot-scrum` por el que prefieras):

docker build -t chatbot-scrum .

## Construcción de la imagen a Docker Hub

Si quieres subir la imagen a Docker Hub, usa tu usuario:

docker build -t TU_USUARIO/chatbot-scrum:latest .

## Ejecución del chatbot

Una vez construida la imagen, ejecuta el contenedor con:

docker run -it --rm chatbot-scrum

## O, si usaste tu usuario de Docker Hub:

docker run -it --rm TU_USUARIO/chatbot-scrum:latest


## Notas

- El chatbot solo responde en la terminal.
- Si necesitas instalar dependencias adicionales, agrégalas al archivo `requirements.txt` y reconstruye la imagen.
- Para detener el chatbot, escribe `salir`, `adiós` o presiona `Ctrl+C`.

Y YERRRRRAAA