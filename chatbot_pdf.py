import requests # Necesario para hacer llamadas HTTP a la API

# --- Configuración de la API de Llama 
# 1. LLAMA_API_URL: Punto final de la API para modelos de chat en Together.ai
#    
LLAMA_API_URL = "https://api.together.xyz/v1/chat/completions"

# 2. LLAMA_API_KEY: Tu clave de API personal de Together.ai
#    
LLAMA_API_KEY = "tgp_v1_4s7dks6_lq2DgCR-n6LcDrB4id9Zf1DGspqEmLswN94"

# 3. LLAMA_MODEL_ID: El identificador exacto del modelo Llama 2 que deseas usar en Together.ai.
#  
LLAMA_MODEL_ID = "meta-llama/Llama-3-70b-chat-hf"


# --- Función Principal (main) ---
def main():
    # --- Verificación de la configuración de la API ---
    if not LLAMA_API_URL or \
       not LLAMA_API_KEY or \
       not LLAMA_MODEL_ID:
        print("ERROR: Por favor, configura LLAMA_API_URL, LLAMA_API_KEY y LLAMA_MODEL_ID con tus valores reales antes de ejecutar.")
        return

    print("Configurando el acceso al modelo Llama a través de la API de Together.ai...")

    print("\nListo. Puedes hacer preguntas y el bot responderá desde la perspectiva de la metodología Scrum,")
    print("usando su conocimiento pre-entrenado.")
    
    while True:
        pregunta = input("\nTú: ")
        if pregunta.lower() in ["adios", "salir", "exit"]:
            print("Chatbot: ¡Hasta luego!")
            break

        # Lógica de respuesta: Usar Llama con el prompt de contexto Scrum, sin contexto del PDF.
        
        # Instrucción principal para que Llama responda desde la perspectiva de Scrum
        prompt_base_scrum = (
            "Eres un experto en la metodología Scrum. Responde siempre a las preguntas desde la perspectiva de Scrum. "
            "Si la pregunta es general, relacionala con los principios, roles, eventos o artefactos de Scrum, o con las prácticas comunes en equipos Scrum. "
            "Si no puedes relacionar la pregunta con Scrum, indica claramente que la pregunta está fuera del alcance de la metodología Scrum o que no puedes responderla desde esa perspectiva."
        )

        messages_for_api = []
        # El rol "system" se usa para establecer el comportamiento del modelo
        messages_for_api.append({"role": "system", "content": prompt_base_scrum})

        # La pregunta del usuario
        messages_for_api.append({"role": "user", "content": pregunta})
        
        headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {LLAMA_API_KEY}" # Tu clave de API aquí
        }

        payload = {
            "model": LLAMA_MODEL_ID, # Usa la variable LLAMA_MODEL_ID aquí
            "messages": messages_for_api,
            "max_tokens": 1024, # Máximo número de tokens en la respuesta
            "stop": [], # Tokens para detener la generación (vacío significa que generará hasta max_tokens)
            "temperature": 0.7 # Controla la creatividad/aleatoriedad de la respuesta (0.0 muy determinista, 1.0 muy creativo)
        }

        print("DEBUG: Enviando al modelo Llama vía API...")
        try:
            response = requests.post(LLAMA_API_URL, headers=headers, json=payload)
            response.raise_for_status() # Lanza un error para códigos de estado HTTP 4xx/5xx
            output = response.json()
            
            respuesta_llama = ""
            # La forma de acceder a la respuesta puede variar ligeramente según la estructura de la API.
            # Este es el formato común para APIs de chat (como OpenAI, Together.ai)
            if output and "choices" in output and len(output["choices"]) > 0 and \
               "message" in output["choices"][0] and "content" in output["choices"][0]["message"]:
                respuesta_llama = output["choices"][0]["message"]["content"].strip()
            elif output and "error" in output: # Manejo de errores de la API
                print(f"Error de API: {output['error'].get('message', 'Mensaje de error desconocido')}")
                respuesta_llama = "Lo siento, hubo un error con la API del modelo."

            # Filtra respuestas vacías o que indican que el modelo no pudo responder desde la perspectiva de Scrum
            if respuesta_llama and len(respuesta_llama) > 10 and \
               "fuera del alcance de la metodología scrum" not in respuesta_llama.lower() and \
               "no puedo proporcionar información" not in respuesta_llama.lower() and \
               "no encontré información" not in respuesta_llama.lower() and \
               "no se menciona" not in respuesta_llama.lower(): 
                
                print(f"Chatbot (Llama - Perspectiva Scrum): {respuesta_llama}")
            else:
                # Si Llama no pudo responder o indicó que no podía, muestra un mensaje por defecto.
                print("Chatbot: Lo siento, no pude encontrar una respuesta relevante sobre Scrum para tu pregunta en este momento. Intenta reformularla.")
                
        except requests.exceptions.RequestException as e:
            # Captura errores relacionados con la conexión HTTP (red, DNS, timeout, etc.)
            print(f"Error en la solicitud a la API: {e}")
            print("Chatbot: Lo siento, hubo un problema de conexión con el servicio del modelo. Por favor, verifica tu conexión a internet y la configuración de la API (URL, clave).")
        except Exception as e:
            # Captura cualquier otro error inesperado durante el procesamiento
            print(f"Error inesperado al procesar la respuesta o al llamar a la API: {e}")
            print("Chatbot: Lo siento, no pude procesar tu solicitud en este momento debido a un error interno.")


if __name__ == "__main__":
    main()
