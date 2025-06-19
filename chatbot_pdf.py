import PyPDF2
from llama_cpp import Llama
import re
from unidecode import unidecode
from fuzzywuzzy import fuzz

PDF_PATH = "2020-Scrum-Guide-Spanish-Latin-South-American.pdf"
LLAMA_MODEL_PATH = "llama-2-13b-chat.Q4_K_M.gguf"  # Asegúrate de que esta ruta sea correcta

# --- Funciones de utilidad (mantener como en la última versión, solo las relevantes aquí para concisión) ---
def clean_text(text):
    text = unidecode(text.lower())
    text = re.sub(r'[^a-zA-Z0-9áéíóúñü\s]', '', text)
    text = re.sub(r'\s+', ' ', text)
    return text.strip()

def extract_paragraphs_from_pdf(pdf_path):
    # Implementación de la función extract_paragraphs_from_pdf (la última versión mejorada)
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

                    if (len(line_stripped) < 5 and not re.search(r'[.!?]', line_stripped)) or \
                       re.match(r'^\d+$', line_stripped) or \
                       re.match(r'^[. -_—–]+$', line_stripped) or \
                       re.search(r'^\s*[\w\s]+\s*[. -_]+\s*\d+\s*$', line_stripped) or \
                       re.search(r'guia de scrum|ken schwaber|jeff sutherland', clean_text(line_stripped), re.IGNORECASE) or \
                       (line_stripped.isupper() and len(line_stripped.split()) < 4):
                        continue
                    
                    current_paragraph_lines.append(line_stripped)
                    
                    if re.search(r'[.!?]$', line_stripped) or len(" ".join(current_paragraph_lines)) > 150:
                        paragraph = " ".join(current_paragraph_lines).strip()
                        if len(paragraph) > 60 and re.search(r'[a-zA-Z]{3,}', paragraph):
                            paragraphs.append(paragraph)
                        current_paragraph_lines = []
                
                if current_paragraph_lines and len(" ".join(current_paragraph_lines)) > 60:
                    paragraphs.append(" ".join(current_paragraph_lines).strip())
    return paragraphs

def find_relevant_paragraphs(question, paragraphs, top_n=3, min_score=0.3):
    # Implementación de la función find_relevant_paragraphs (la última versión)
    from sklearn.feature_extraction.text import TfidfVectorizer
    from sklearn.metrics.pairwise import cosine_similarity
    
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
    # Implementación de la función buscar_definicion_entidad (la última versión)
    pregunta_limpia = clean_text(pregunta)
    match = re.search(r"(?:que|qué|defineme|define|significa)\s+(?:es|es\s+el|es\s+la|es\s+un|es\s+una)?\s*([a-z0-9\s]+)", pregunta_limpia)
    
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
            if len(def_cand.split()) >= 8 and len(def_cand.split()) <= 60 and re.search(r'[.!?]$', def_cand.strip()):
                return def_cand.strip()
        if posibles_definiciones:
            return posibles_definiciones[0].strip()
    
    return None

def buscar_apartado_entidad(pregunta, sections):
    # Implementación de la función buscar_apartado_entidad (la última versión)
    import re
    pregunta_limpia = clean_text(pregunta)
    
    match = re.search(r"(?:que es|qué es|sobre|háblame de|dónde está|dame información de)\s+([a-z0-9\s]+)", pregunta_limpia)
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

SECTION_TITLES = [
    "Propósito de la Guía Scrum", "Definición de Scrum", "Teoría de Scrum", "Transparencia",
    "Inspección", "Adaptación", "Valores de Scrum", "Scrum Team", "Developers", "Product Owner",
    "Scrum Master", "Eventos de Scrum", "El Sprint", "Sprint Planning", "Daily Scrum",
    "Sprint Review", "Sprint Retrospective", "Artefactos de Scrum", "Product Backlog",
    "Compromiso: Objetivo del Producto", "Sprint Backlog", "Compromiso: Objetivo del Sprint",
    "Increment", "Compromiso: Definición de Terminado", "Nota final", "Agradecimientos", "Personas",
    "Historia de la Guía de Scrum", "Traducción", "Cambios de la Guía Scrum 2017 a la Guía Scrum 2020"
]

def clean_section_title(title):
    import re
    t = title.lower()
    t = re.sub(r'[.·…_\-]+', '', t)
    t = re.sub(r'\s+', ' ', t)
    t = t.strip()
    return t

def extract_sections_from_pdf(pdf_path):
    # Implementación de la función extract_sections_from_pdf (la última versión)
    from fuzzywuzzy import fuzz
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
                
        if best_score >= 85: 
            if current_section:
                sections[current_section] = section_content
            current_section = best_title
            section_content = []
        elif current_section:
            if len(line.strip()) > 5 and not re.match(r'^\d+$', line.strip()):
                section_content.append(line)
                
    if current_section: 
        sections[current_section] = section_content
    return sections


# --- Función Principal (main) - Modificada para el comportamiento de fallback ---
def main():
    print("Cargando modelo Llama, esto puede tardar unos minutos la primera vez...")
    try:
        llm = Llama(model_path=LLAMA_MODEL_PATH, n_ctx=2048, n_threads=8)
    except Exception as e:
        print(f"Error al cargar el modelo Llama: {e}. Asegúrate de que '{LLAMA_MODEL_PATH}' esté en la ruta correcta.")
        return

    print("Extrayendo texto del PDF...")
    paragraphs = extract_paragraphs_from_pdf(PDF_PATH)
    sections = extract_sections_from_pdf(PDF_PATH)
    
    print("Apartados detectados en el PDF:")
    for idx, title in enumerate(sections.keys()):
        print(f"  {idx+1}. {title}")
    print("Listo. Puedes hacer preguntas sobre Scrum y el bot responderá usando el modelo Llama.")
    
    while True:
        pregunta = input("Tú: ")
        if pregunta.lower() in ["adiós", "salir", "exit"]:
            print("Chatbot: ¡Hasta luego!")
            break

        # 1. Intentar buscar una definición directa y concisa en el PDF
        definicion_encontrada = buscar_definicion_entidad(pregunta, paragraphs)
        if definicion_encontrada:
            print(f"Chatbot (Definición del PDF): {definicion_encontrada}")
            continue 

        # 2. Si no es una definición directa, intentar buscar el apartado completo en el PDF
        apartado = buscar_apartado_entidad(pregunta, sections)
        if apartado:
            print(f"Chatbot (Apartado Completo del PDF): {apartado}") 
            continue

        # 3. Si no hay información relevante del PDF (ni definición ni apartado),
        #    intentar usar los párrafos más relevantes como contexto para Llama.
        #    Si incluso con el contexto Llama dice que no sabe, entonces se usa
        #    el conocimiento general de Llama.
        
        contexto_del_pdf = "\n".join(find_relevant_paragraphs(pregunta, paragraphs, top_n=3, min_score=0.3)) 
        
        respuesta_llama_con_contexto = None
        if contexto_del_pdf:
            prompt_con_contexto = f"Basándote en el siguiente texto de la Guía de Scrum, responde a la pregunta de manera concisa y clara. Si la información no está presente en este texto, indica que no la sabes. \n\nContexto:\n{contexto_del_pdf}\n\nPregunta: {pregunta}\nRespuesta:"
            print("DEBUG: Enviando al modelo Llama con contexto de párrafos relevantes del PDF...")
            try:
                output = llm(prompt_con_contexto, max_tokens=256, stop=["\n", "Respuesta:", "Pregunta:"], echo=False)
                respuesta_llama_con_contexto = output["choices"][0]["text"].strip()
                # Verificar si Llama realmente dio una respuesta o dijo que no sabía basado en el contexto
                if respuesta_llama_con_contexto and len(respuesta_llama_con_contexto) > 10 and \
                   "no sé" not in respuesta_llama_con_contexto.lower() and \
                   "no encontré" not in respuesta_llama_con_contexto.lower() and \
                   "no está en este texto" not in respuesta_llama_con_contexto.lower():
                    
                    print(f"Chatbot (Llama con Contexto del PDF): {respuesta_llama_con_contexto}")
                    continue
            except Exception as e:
                print(f"Error al llamar a Llama con contexto: {e}")
        
        # 4. Si ninguna de las estrategias anteriores funcionó (ni definición, ni apartado, ni Llama con contexto del PDF dio una respuesta válida),
        #    entonces recurrimos al conocimiento general de Llama, sin forzar un contexto del PDF.
        print("DEBUG: No se encontró información específica en el PDF. Recurriendo al conocimiento general de Llama...")
        try:
            # Quitamos la instrucción de basarse solo en el texto del PDF
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