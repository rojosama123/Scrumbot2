import requests

LLAMA_API_URL = "https://api.together.xyz/v1/chat/completions"
LLAMA_API_KEY = "tgp_v1_4s7dks6_lq2DgCR-n6LcDrB4id9Zf1DGspqEmLswN94"
LLAMA_MODEL_ID = "meta-llama/Llama-3-70b-chat-hf"

def enviar_a_llama(pregunta: str) -> str:
    prompt_base_scrum = (
        "Eres un experto en la metodología Scrum. Responde siempre a las preguntas desde la perspectiva de Scrum. "
        "Si la pregunta es general, relacionala con los principios, roles, eventos o artefactos de Scrum, o con las prácticas comunes en equipos Scrum. "
        "Si no puedes relacionar la pregunta con Scrum, indica claramente que la pregunta está fuera del alcance de la metodología Scrum o que no puedes responderla desde esa perspectiva."
    )
    
    messages_for_api = [
        {"role": "system", "content": prompt_base_scrum},
        {"role": "user", "content": pregunta}
    ]

    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {LLAMA_API_KEY}"
    }

    payload = {
        "model": LLAMA_MODEL_ID,
        "messages": messages_for_api,
        "max_tokens": 1024,
        "temperature": 0.7
    }

    try:
        response = requests.post(LLAMA_API_URL, headers=headers, json=payload)
        response.raise_for_status()
        output = response.json()

        if output and "choices" in output and len(output["choices"]) > 0 and \
           "message" in output["choices"][0] and "content" in output["choices"][0]["message"]:
            respuesta = output["choices"][0]["message"]["content"].strip()
        elif output and "error" in output:
            respuesta = "Lo siento, hubo un error con la API del modelo."
        else:
            respuesta = "No se obtuvo una respuesta válida del modelo."

        # Filtro para evitar respuestas no relacionadas con Scrum
        if respuesta and len(respuesta) > 10 and \
           "fuera del alcance de la metodología scrum" not in respuesta.lower():
            return respuesta
        else:
            return "Lo siento, no pude encontrar una respuesta relevante sobre Scrum para tu pregunta. Intenta reformularla."

    except requests.exceptions.RequestException as e:
        return "Lo siento, hubo un problema de conexión con el servicio del modelo."
    except Exception as e:
        return "Lo siento, no pude procesar tu solicitud debido a un error interno."

