from flask import Flask, render_template, request
import requests
import markdown # <-- Asegúrate de que esta línea esté aquí

app = Flask(__name__)

# Configuración de la API de Llama (usa tus valores reales)
LLAMA_API_URL = "https://api.together.xyz/v1/chat/completions"
LLAMA_API_KEY = "tgp_v1_SNMu486Mr8vuOIebx9uL2TZpwKr5TUL5SfuKjwPUHrA" # <--- ¡PON TU CLAVE REAL AQUÍ!
LLAMA_MODEL_ID = "meta-llama/Llama-3-70b-chat-hf"

PROMPT_SCRUM = (
    "Eres un experto en la metodología Scrum. Responde siempre a las preguntas desde la perspectiva de Scrum. "
    "Si la pregunta es general, relacionala con los principios, roles, eventos o artefactos de Scrum, o con las prácticas comunes en equipos Scrum. "
    "**Formatea tus respuestas EXCLUSIVAMENTE usando sintaxis Markdown para mejorar la legibilidad. NO uses NINGUNA etiqueta HTML directamente.** "
    "Utiliza encabezados (##, ###), listas con viñetas (- o *), listas numeradas (1., 2.), negritas (**texto**), y saltos de línea para estructurar la información. "
    "Sé conciso y ve directo al punto, presentando la información de manera clara y estructurada."
    "Si no puedes relacionar la pregunta con Scrum, indica claramente que la pregunta está fuera del alcance de la metodología Scrum o que no puedes responderla desde esa perspectiva."
)

@app.route("/", methods=["GET", "POST"])
def index():
    respuesta_html = ""
    if request.method == "POST":
        pregunta = request.form["pregunta"]
        messages_for_api = [
            {"role": "system", "content": PROMPT_SCRUM},
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
            "stop": [],
            "temperature": 0.7
        }
        try:
            response = requests.post(LLAMA_API_URL, headers=headers, json=payload)
            response.raise_for_status()
            output = response.json()
            if output and "choices" in output and len(output["choices"]) > 0 and \
               "message" in output["choices"][0] and "content" in output["choices"][0]["message"]:
                respuesta_markdown = output["choices"][0]["message"]["content"].strip()
                # ¡Convertimos Markdown a HTML aquí!
                respuesta_html = markdown.markdown(respuesta_markdown) # <-- Asegúrate de que esta línea esté aquí
            else:
                respuesta_html = "No se pudo obtener respuesta del modelo."
        except Exception as e:
            respuesta_html = f"Error: {e}"
    return render_template("index.html", respuesta=respuesta_html)

if __name__ == "__main__":
    app.run(debug=True)