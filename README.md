# Chatbot basico
Este chatbot funciona unicamente en terminal, por ahora.

Para hacerlo funcionar deben hacer lo de abajo.


## Instalación de Docker Desktop

1. Ingresar a la pagina oficial de Docker y descargar el DockerDesktop
2. Ejecutar el instalador e iniciar sesión 
3. Deberían ver la imagen en el Docker Hub


## Construcción de la imagen a Docker Hub

Primero siempre tiene que iniciar sesión por terminal

docker login

Luego, para subir la imagen a Docker Hub, usa tu usuario:

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