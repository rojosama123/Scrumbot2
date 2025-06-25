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

## Instalación de dependencias del proyecto

1. Abre una terminal dentro de Visual Studio en la carpeta raiz (menú "Ver > Terminal").
2. Ejecuta:
   ```
   pip install -r requirements.txt
   ```

## Descarga del modelo Llama 2 (llama-2-13b-chat.Q4_K_M.gguf)

Para que el chatbot funcione correctamente, necesitas descargar el modelo Llama 2 en formato GGUF:

1. Ve al siguiente enlace: [Descargar modelo Llama 2 - GGUF (Hugging Face)](https://huggingface.co/TheBloke/Llama-2-13B-chat-GGUF/blob/main/llama-2-13b-chat.Q4_K_M.gguf)
2. Haz clic en el botón "Download" junto al archivo `llama-2-13b-chat.Q4_K_M.gguf`.
3. Guarda el archivo descargado en la carpeta raíz de este proyecto (`chatbot2`).
4. Verifica que la ruta y el nombre del archivo coincidan exactamente con lo que espera el script (`llama-2-13b-chat.Q4_K_M.gguf`).

## Cómo iniciar el chatbot

Para iniciar el chatbot y comenzar a interactuar con él, sigue estos pasos:

1. Abre una terminal en la carpeta del proyecto (`chatbot2`).
2. Ejecuta el siguiente comando para el chatbot básico:
   ```
   python chatbot_pdf.py
   ```
3. Escribe tus preguntas en la consola y presiona Enter para recibir respuestas.
4. Para salir, escribe `salir`, `adiós` o `exit` y presiona Enter.


