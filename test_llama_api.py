import requests

LLAMA_API_URL = "https://api.together.xyz/v1/chat/completions"
LLAMA_API_KEY = "tgp_v1_4s7dks6_lq2DgCR-n6LcDrB4id9Zf1DGspqEmLswN94"  # Pon aquí tu API key real
LLAMA_MODEL_ID = "meta-llama/Llama-3-70b-chat-hf"

def enviar_a_llama(pregunta):
    prompt_base = "Eres un experto en la metodología Scrum. Responde desde esa perspectiva."
    messages = [
        {"role": "system", "content": prompt_base},
        {"role": "user", "content": pregunta}
    ]

    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {LLAMA_API_KEY}"
    }

    payload = {
        "model": LLAMA_MODEL_ID,
        "messages": messages,
        "max_tokens": 1024,
        "temperature": 0.7
    }

    try:
        response = requests.post(LLAMA_API_URL, headers=headers, json=payload, timeout=15)
        response.raise_for_status()
        data = response.json()
        if "choices" in data and len(data["choices"]) > 0:
            return data["choices"][0]["message"]["content"].strip()
        else:
            return "No se recibió respuesta válida del modelo."
    except Exception as e:
        return f"Error al llamar a la API: {e}"

if __name__ == "__main__":
    pregunta = "¿Qué es un Sprint?"
    respuesta = enviar_a_llama(pregunta)
    print("Pregunta:", pregunta)
    print("Respuesta:", respuesta)
