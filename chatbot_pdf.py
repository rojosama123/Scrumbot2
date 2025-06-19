import PyPDF2
from llama_cpp import Llama
import re
from unidecode import unidecode
from fuzzywuzzy import fuzz
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

# --- Rutas a tus archivos ---
PDF_PATH = "2020-Scrum-Guide-Spanish-Latin-South-American.pdf"
LLAMA_MODEL_PATH = "llama-2-13b-chat.Q4_K_M.gguf"  # Asegúrate de que esta ruta sea correcta

# --- Lista de títulos de secciones conocidos en la Guía Scrum ---
SECTION_TITLES = [
    "Propósito de la Guía Scrum", "Definición de Scrum", "Teoría de Scrum", "Transparencia",
    "Inspección", "Adaptación", "Valores de Scrum", "Scrum Team", "Developers", "Product Owner",
    "Scrum Master", "Eventos de Scrum", "El Sprint", "Sprint Planning", "Daily Scrum",
    "Sprint Review", "Sprint Retrospective", "Artefactos de Scrum", "Product Backlog",
    "Compromiso: Objetivo del Producto", "Sprint Backlog", "Compromiso: Objetivo del Sprint",
    "Increment", "Compromiso: Definición de Terminado", "Nota final", "Agradecimientos", "Personas",
    "Historia de la Guía de Scrum", "Traducción", "Cambios de la Guía Scrum 2017 a la Guía Scrum 2020"
]

# --- Funciones de utilidad ---

def clean_text(text):
    """Limpia el texto: minúsculas, quita acentos, elimina caracteres no alfanuméricos y espacios extra."""
    text = unidecode(text.lower())
    text = re.sub(r'[^a-zA-Z0-9áéíóúñü\s]', '', text)
    text = re.sub(r'\s+', ' ', text)
    return text.strip()

def clean_section_title(title):
    """Limpia un título de sección para comparación."""
    t = title.lower()
    t = re.sub(r'[.·…_\-]+', '', t) # Elimina puntos, guiones, etc.
    t = re.sub(r'\s+', ' ', t)     # Normaliza espacios
    t = t.strip()
    return t

def extract_paragraphs_from_pdf(pdf_path):
    """Extrae párrafos del PDF, filtrando elementos no deseados como números de página o encabezados."""
    paragraphs = []
    with open(pdf_path, "rb") as file:
        reader = PyPDF2.PdfReader(file)
        for page_num in range(len(reader.pages)):
            page = reader.pages[page_num]
            text = page.extract_text()
            if text:
                lines = text.split("\n")
                current_paragraph_lines = []
                for line in lines:
                    line_stripped = line.strip()

                    # Criterios para saltar líneas que no son parte de párrafos normales
                    if (len(line_stripped) < 5 and not re.search(r'[.!?]', line_stripped)) or \
                       re.match(r'^\d+$', line_stripped) or \
                       re.match(r'^[. -_—–]+$', line_stripped) or \
                       re.search(r'^\s*[\w\s]+\s*[. -_]+\s*\d+\s*$', line_stripped) or \
                       re.search(r'guia de scrum|ken schwaber|jeff sutherland', clean_text(line_stripped), re.IGNORECASE) or \
                       (line_stripped.isupper() and len(line_stripped.split()) < 4):
                        continue
                    
                    current_paragraph_lines.append(line_stripped)
                    
                    # Criterio para finalizar un párrafo (puntuación o longitud máxima)
                    if re.search(r'[.!?]$', line_stripped) or len(" ".join(current_paragraph_lines)) > 150:
                        paragraph = " ".join(current_paragraph_lines).strip()
                        # Solo añade párrafos que sean sustanciales
                        if len(paragraph) > 60 and re.search(r'[a-zA-Z]{3,}', paragraph):
                            paragraphs.append(paragraph)
                        current_paragraph_lines = []
                
                # Añadir cualquier párrafo incompleto al final de la página si es sustancial
                if current_paragraph_lines and len(" ".join(current_paragraph_lines)) > 60:
                    paragraphs.append(" ".join(current_paragraph_lines).strip())
    return paragraphs

def extract_sections_from_pdf(pdf_path):
    """Extrae contenido del PDF organizado por las secciones definidas en SECTION_TITLES."""
    sections = {}
    with open(pdf_path, "rb") as file:
        reader = PyPDF2.PdfReader(file)
        all_text = []
        for page in reader.pages:
            text = page.extract_text()
            if text:
                all_text.extend([line.strip() for line in text.split("\n") if line.strip()])
                
    current_section = None
    section_content = []
    clean_titles = [clean_section_title(t) for t in SECTION_TITLES]
    
    for line in all_text:
        line_clean = clean_section_title(line)
        best_title = None
        best_score = 0
        
        for t, t_clean in zip(SECTION_TITLES, clean_titles):
            score = fuzz.ratio(line_clean, t_clean)
            if score > best_score:
                best_score = score
                best_title = t
                
        if best_score >= 85: # Umbral alto para coincidencia de título de sección
            if current_section: # Guardar la sección anterior antes de empezar una nueva
                sections[current_section] = section_content
            current_section = best_title
            section_content = []
        elif current_section: # Si estamos dentro de una sección, añadir la línea a su contenido
            if len(line.strip()) > 5 and not re.match(r'^\d+$', line.strip()): # Ignorar líneas muy cortas o solo números (posibles pies de página)
                section_content.append(line)
                
    if current_section: # Asegurarse de añadir la última sección
        sections[current_section] = section_content
    return sections

def find_relevant_paragraphs(question, paragraphs, top_n=3, min_score=0.3):
    """
    Encuentra los párrafos más relevantes a una pregunta usando similitud coseno de TF-IDF.
    Devuelve una lista de los párrafos más relevantes.
    """
    clean_paragraphs = [clean_text(p) for p in paragraphs]
    question_clean = clean_text(question)
    
    if not clean_paragraphs or not question_clean.strip():
        return []

    all_texts = clean_paragraphs + [question_clean]
    vectorizer = TfidfVectorizer()
    try:
        vectorizer.fit(all_texts)
    except ValueError:
        return []

    if not vectorizer.vocabulary_:
        return []

    para_vectors = vectorizer.transform(clean_paragraphs)
    question_vector = vectorizer.transform([question_clean])
    
    similarities = cosine_similarity(question_vector, para_vectors).flatten()
    
    best_indices = [i for i in similarities.argsort()[::-1] if similarities[i] >= min_score]
    return [paragraphs[idx] for idx in best_indices[:top_n]]

def buscar_definicion_entidad(pregunta, paragraphs, min_fuzz_score=80):
    """
    Busca una definición concisa de una entidad en los párrafos.
    Prioriza oraciones que contienen "es", "se define como", etc.
    """
    pregunta_limpia = clean_text(pregunta)
    match = re.search(r"(?:que|qué|defineme|define|significa|es)\s+(?:es|es\s+el|es\s+la|es\s+un|es\s+una)?\s*([a-z0-9áéíóúñü\s]+)", pregunta_limpia)
    
    entidad = None
    if match:
        entidad = match.group(1).strip()
        entidad = re.sub(r"^(el|la|los|las|un|una|unos|unas)\s+", "", entidad).strip()
    
    if not entidad:
        return None 
        
    print(f"DEBUG: Intentando definir la entidad: '{entidad}'") 
    
    posibles_definiciones = []
    
    for p in paragraphs:
        p_limpio = clean_text(p)
        
        if fuzz.partial_ratio(entidad, p_limpio) < min_fuzz_score:
            continue
            
        sentences = re.split(r'(?<=[.!?])\s+', p)
        for sentence in sentences:
            sentence_clean = clean_text(sentence)
            
            if fuzz.partial_ratio(entidad, sentence_clean) < min_fuzz_score:
                continue

            match_es = re.search(r"\b" + re.escape(entidad) + r"\b\s*(?:es|son|\(es\))\s*([^.]+\.)", sentence, re.IGNORECASE)
            if match_es:
                posibles_definiciones.append(match_es.group(0).strip())
                continue
                
            match_define = re.search(r"\b" + re.escape(entidad) + r"\b(?:,|)\s*(?:se define como|consiste en|tiene el propósito de|es el objetivo de)\s*([^.]+\.)", sentence, re.IGNORECASE)
            if match_define:
                posibles_definiciones.append(match_define.group(0).strip())
                continue

            if sentence_clean.startswith(entidad) and len(sentence.split()) <= 40:
                if re.search(r'\b(?:es|son|define|consiste|sirve|permite|ayuda|crea|mejora|objetivo)\b', sentence_clean):
                    posibles_definiciones.append(sentence.strip())

    posibles_definiciones = list(dict.fromkeys(posibles_definiciones)) 
    posibles_definiciones.sort(key=lambda x: len(x)) 

    if posibles_definiciones:
        for def_cand in posibles_definiciones:
            if 8 <= len(def_cand.split()) <= 60 and re.search(r'[.!?]$', def_cand.strip()):
                return def_cand.strip()
        if posibles_definiciones:
            return posibles_definiciones[0].strip()
    
    return None

def buscar_apartado_entidad(pregunta, sections):
    """
    Busca si la pregunta se refiere a un apartado completo del PDF.
    Devuelve el contenido completo del apartado si lo encuentra.
    """
    pregunta_limpia = clean_text(pregunta)
    
    match = re.search(r"(?:que es|qué es|sobre|háblame de|dónde está|dame información de)\s+([a-z0-9áéíóúñü\s]+)", pregunta_limpia)
    if match:
        entidad = match.group(1).strip()
        entidad = re.sub(r"^(el|la|los|las|un|una|unos|unas)\s+", "", entidad).strip()
    else:
        entidad = pregunta_limpia 
        
    print(f"DEBUG: Intentando buscar apartado para: '{entidad}'") 
    
    section_titles = list(sections.keys())
    clean_titles = [clean_section_title(t) for t in section_titles]
    
    best_score = 0
    best_idx = -1
    for i, t_clean in enumerate(clean_titles):
        score = fuzz.ratio(entidad, t_clean)
        if score > best_score:
            best_score = score
            best_idx = i
            
    if best_score > 75:
        best_section_title = section_titles[best_idx]
        contenido = '\n'.join(sections[best_section_title])
        return f"**{best_section_title}**\n{contenido}"
    return None

# --- Función Principal (main) ---
def main():
    print("Cargando modelo Llama, esto puede tardar unos minutos la primera vez...")
    try:
        llm = Llama(model_path=LLAMA_MODEL_PATH, n_ctx=2048, n_threads=8)
    except Exception as e:
        print(f"Error al cargar el modelo Llama: {e}. Asegúrate de que '{LLAMA_MODEL_PATH}' esté en la ruta correcta y que tienes las dependencias instaladas (llama-cpp-python).")
        return

    print("Extrayendo texto del PDF...")
    paragraphs = extract_paragraphs_from_pdf(PDF_PATH)
    sections = extract_sections_from_pdf(PDF_PATH)
    
    print("Apartados detectados en el PDF:")
    for idx, title in enumerate(sections.keys()):
        print(f"  {idx+1}. {title}")
    print("Listo. Puedes hacer preguntas sobre Scrum y el bot responderá.")
    
    while True:
        pregunta = input("Tú: ")
        if pregunta.lower() in ["adiós", "salir", "exit"]:
            print("Chatbot: ¡Hasta luego!")
            break

        # --- Flujo de Respuestas (Priorizado: Apartado > Definición > RAG > Llama General) ---

        # 1. Prioridad: Buscar el apartado completo en el PDF
        apartado = buscar_apartado_entidad(pregunta, sections)
        if apartado:
            print(f"Chatbot (Apartado Completo del PDF): {apartado}") 
            continue # Si se encuentra un apartado, termina aquí y espera nueva pregunta.

        # 2. Segunda prioridad: Buscar una definición directa y concisa en el PDF
        definicion_encontrada = buscar_definicion_entidad(pregunta, paragraphs)
        if definicion_encontrada:
            print(f"Chatbot (Definición del PDF): {definicion_encontrada}")
            continue # Si se encuentra una definición, termina aquí y espera nueva pregunta.

        # 3. Tercera prioridad: Si no hay definición ni apartado directo, usar Llama con contexto de los párrafos más relevantes del PDF (RAG)
        contexto_del_pdf_list = find_relevant_paragraphs(pregunta, paragraphs, top_n=3, min_score=0.2) 
        contexto_para_llama = "\n".join(contexto_del_pdf_list)
        
        respuesta_llama_con_contexto = None
        if contexto_para_llama.strip(): # Si se encontró algún párrafo relevante
            prompt_con_contexto = f"Basándote en el siguiente texto de la Guía de Scrum, responde a la pregunta de manera concisa y clara. Si la información no está presente en este texto, indica que no la sabes. \n\nContexto:\n{contexto_para_llama}\n\nPregunta: {pregunta}\nRespuesta:"
            print("DEBUG: Enviando al modelo Llama con contexto de párrafos relevantes del PDF...")
            try:
                output = llm(prompt_con_contexto, max_tokens=1024, stop=[], echo=False) 
                respuesta_llama_con_contexto = output["choices"][0]["text"].strip()
                
                if respuesta_llama_con_contexto and len(respuesta_llama_con_contexto) > 10 and \
                   "no sé" not in respuesta_llama_con_contexto.lower() and \
                   "no encontré" not in respuesta_llama_con_contexto.lower() and \
                   "no está en este texto" not in respuesta_llama_con_contexto.lower() and \
                   "no se menciona" not in respuesta_llama_con_contexto.lower() and \
                   "no hay información" not in respuesta_llama_con_contexto.lower():
                    
                    print(f"Chatbot (Llama con Contexto del PDF): {respuesta_llama_con_contexto}")
                    continue
            except Exception as e:
                print(f"Error al llamar a Llama con contexto: {e}")
        
        # 4. Fallback: Si ninguna de las estrategias anteriores funcionó, recurrimos al conocimiento general de Llama.
        print("DEBUG: No se encontró información específica en el PDF. Recurriendo al conocimiento general de Llama...")
        try:
            prompt_general = f"Responde a la siguiente pregunta: {pregunta}\nRespuesta:"
            output_general = llm(prompt_general, max_tokens=1024, stop=[], echo=False)
            respuesta_general_llama = output_general["choices"][0]["text"].strip()
            
            if respuesta_general_llama and len(respuesta_general_llama) > 10:
                print(f"Chatbot (Llama - Conocimiento General): {respuesta_general_llama}")
            else:
                print("Chatbot: Lo siento, no tengo información sobre eso, ni en la Guía de Scrum ni en mi conocimiento general.")
        except Exception as e:
            print(f"Error al llamar a Llama (conocimiento general): {e}")
            print("Chatbot: Lo siento, no pude procesar tu solicitud en este momento.")


if __name__ == "__main__":
    main()