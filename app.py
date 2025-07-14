import os
import json
import requests
import markdown
from flask import Flask, render_template, request, redirect, url_for, session, flash
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import LoginManager, UserMixin, login_user, login_required, logout_user, current_user

app = Flask(__name__)
app.config['SECRET_KEY'] = 'tu_super_secreto_aqui_cambialo_en_produccion_mas_complejo' # ¡IMPORTANTE! Cambia esto por una clave compleja y segura
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///site.db' # Ruta de la base de datos SQLite
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)
login_manager = LoginManager(app)
login_manager.login_view = 'index' # Redirige a la página principal si no está logueado

# Configuración de la API de Llama (usa tus valores reales)
LLAMA_API_URL = "https://api.together.xyz/v1/chat/completions"
LLAMA_API_KEY = "tgp_v1_8FWQQUlSrxg_-JA09jTr6xXeDrJwV3d3GE6P9zNjaK0" # <--- ¡PON TU CLAVE REAL AQUÍ!
LLAMA_MODEL_ID = "meta-llama/Llama-3-70b-chat-hf"

# Prompt del chatbot mejorado
PROMPT_SCRUM = (
    "Eres un experto en la metodología Scrum. Responde siempre a las preguntas desde la perspectiva de Scrum. "
    "Si la pregunta es general, relacionala con los principios, roles, eventos o artefactos de Scrum, o con las prácticas comunes en equipos Scrum. "
    "**Formatea tus respuestas EXCLUSIVAMENTE usando sintaxis Markdown para mejorar la legibilidad. NO uses NINGUNA etiqueta HTML directamente.** "
    "Utiliza encabezados (##, ###), listas con viñetas (- o *), listas numeradas (1., 2.), negritas (**texto**), y saltos de línea para estructurar la información. "
    "Sé conciso y ve directo al punto, presentando la información de manera clara y estructurada. "
    "Si no puedes relacionar la pregunta con Scrum, indica claramente que la pregunta está fuera del alcance de la metodología Scrum o que no puedes responderla desde esa perspectiva."
)

# --- Modelos de Base de Datos ---
class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    password_hash = db.Column(db.String(128), nullable=False)
    tasks = db.relationship('Task', backref='author', lazy=True)
    impediments = db.relationship('Impediment', backref='reporter', lazy=True)

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

    def __repr__(self):
        return f"User('{self.username}')"

class Task(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(200), nullable=False)
    details = db.Column(db.Text, nullable=True)
    status = db.Column(db.String(50), default='pendiente') # Ej: 'pendiente', 'en progreso', 'completada'
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)

    def __repr__(self):
        return f"Task('{self.name}', '{self.status}')"

class Impediment(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    description = db.Column(db.Text, nullable=False)
    responsible = db.Column(db.String(100), nullable=True)
    status = db.Column(db.String(50), default='abierto') # Ej: 'abierto', 'en resolución', 'resuelto'
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)

    def __repr__(self):
        return f"Impediment('{self.description}', '{self.status}')"

# --- Callbacks de Flask-Login ---
@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

# --- Autenticación y Registro ---

@app.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('index'))

    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        user = User.query.filter_by(username=username).first()
        if user and user.check_password(password):
            login_user(user)
            flash('¡Has iniciado sesión exitosamente!', 'success')
            return redirect(url_for('index'))
        else:
            flash('Inicio de sesión fallido. Verifica tu usuario y contraseña.', 'danger')
            return redirect(url_for('index', show_login_modal=True, login_error="Credenciales incorrectas."))
    return redirect(url_for('index')) # Si GET, redirige al home que mostrará el modal

@app.route('/register', methods=['GET', 'POST'])
def register():
    if current_user.is_authenticated:
        return redirect(url_for('index'))

    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        user = User.query.filter_by(username=username).first()
        if user:
            flash('El nombre de usuario ya existe. Por favor, elige otro.', 'danger')
            return redirect(url_for('index', show_register_modal=True, register_error="El nombre de usuario ya existe."))
        else:
            new_user = User(username=username)
            new_user.set_password(password)
            db.session.add(new_user)
            db.session.commit()
            login_user(new_user)
            flash('¡Tu cuenta ha sido creada y has iniciado sesión!', 'success')
            return redirect(url_for('index'))
    return redirect(url_for('index')) # Si GET, redirige al home que mostrará el modal

@app.route('/logout')
@login_required # Solo permite cerrar sesión si ya está logueado
def logout():
    logout_user()
    flash('Has cerrado sesión.', 'info')
    return redirect(url_for('index'))

# --- Rutas para la gestión de Tareas e Impedimentos ---

@app.route('/tareas', methods=['GET'])
@login_required
def listar_tareas():
    tareas = Task.query.filter_by(user_id=current_user.id).order_by(Task.id.desc()).all()
    return render_template('tareas.html', tareas=tareas)

@app.route('/tareas/modificar/<int:task_id>', methods=['GET', 'POST'])
@login_required
def modificar_tarea(task_id):
    tarea = Task.query.filter_by(id=task_id, user_id=current_user.id).first_or_404()

    if request.method == 'POST':
        tarea.name = request.form.get('name')
        tarea.details = request.form.get('details')
        tarea.status = request.form.get('status')
        db.session.commit()
        flash('Tarea modificada con éxito.', 'success')
        return redirect(url_for('listar_tareas'))
    
    return render_template('modificar_tarea.html', tarea=tarea)

@app.route('/tareas/eliminar/<int:task_id>', methods=['POST'])
@login_required
def eliminar_tarea(task_id):
    tarea = Task.query.filter_by(id=task_id, user_id=current_user.id).first_or_404()
    db.session.delete(tarea)
    db.session.commit()
    flash('Tarea eliminada con éxito.', 'success')
    return redirect(url_for('listar_tareas'))

@app.route('/impedimentos', methods=['GET'])
@login_required
def listar_impedimentos():
    impedimentos = Impediment.query.filter_by(user_id=current_user.id).order_by(Impediment.id.desc()).all()
    return render_template('impedimentos.html', impedimentos=impedimentos)

@app.route('/impedimentos/modificar/<int:impediment_id>', methods=['GET', 'POST'])
@login_required
def modificar_impedimento(impediment_id):
    impedimento = Impediment.query.filter_by(id=impediment_id, user_id=current_user.id).first_or_404()

    if request.method == 'POST':
        impedimento.description = request.form.get('description')
        impedimento.responsible = request.form.get('responsible')
        impedimento.status = request.form.get('status')
        db.session.commit()
        flash('Impedimento modificado con éxito.', 'success')
        return redirect(url_for('listar_impedimentos'))
    
    return render_template('modificar_impedimento.html', impedimento=impedimento)

@app.route('/impedimentos/eliminar/<int:impediment_id>', methods=['POST'])
@login_required
def eliminar_impedimento(impediment_id):
    impedimento = Impediment.query.filter_by(id=impediment_id, user_id=current_user.id).first_or_404()
    db.session.delete(impedimento)
    db.session.commit()
    flash('Impedimento eliminado con éxito.', 'success')
    return redirect(url_for('listar_impedimentos'))

# --- Funcionalidades del Chatbot (Ruta principal) ---

@app.route("/", methods=["GET", "POST"])
def index():
    respuesta_html = ""
    show_login_modal = False
    show_register_modal = False
    
    # Comprobamos si el usuario está autenticado al cargar la página
    if not current_user.is_authenticated:
        show_login_modal = True

    # Para mostrar mensajes flash (éxito, error, etc.)
    # Se usa session.pop para limpiar los mensajes después de leerlos
    messages = []
    for category, message in session.pop('_flashes', []):
        messages.append({'category': category, 'message': message})

    # Si hay errores de login/registro pasados como parámetros de URL
    if request.args.get('login_error'):
        show_login_modal = True
        messages.append({'category': 'danger', 'message': request.args.get('login_error')})
    if request.args.get('register_error'):
        show_register_modal = True
        messages.append({'category': 'danger', 'message': request.args.get('register_error')})


    # Si no está logueado, no procesa preguntas del chatbot, solo muestra el modal
    if not current_user.is_authenticated:
        return render_template("index.html", show_login_modal=show_login_modal,
                               show_register_modal=show_register_modal, messages=messages, current_user=current_user)

    # Manejo del estado para preguntas adicionales (ej. detalles de tarea, responsable de impedimento)
    if 'chatbot_state' not in session:
        session['chatbot_state'] = {'action': None, 'data': {}}

    if request.method == "POST":
        pregunta = request.form.get("pregunta", "").strip()

        # --- Lógica de procesamiento de comandos internos ---
        if session['chatbot_state']['action'] == 'add_task_details':
            # Procesa los detalles adicionales de la tarea
            task_name = session['chatbot_state']['data']['task_name']
            details = pregunta if pregunta else "Sin detalles adicionales."
            
            new_task = Task(name=task_name, details=details, user_id=current_user.id)
            db.session.add(new_task)
            db.session.commit()
            
            respuesta_html = markdown.markdown(f"**Tarea '{task_name}' agregada con los detalles: '{details}'.**")
            session['chatbot_state'] = {'action': None, 'data': {}} # Reinicia el estado
        
        elif session['chatbot_state']['action'] == 'add_impediment_responsible':
            # Procesa el responsable del impedimento
            impediment_description = session['chatbot_state']['data']['impediment_description']
            responsible = pregunta if pregunta else "No asignado."
            
            new_impediment = Impediment(description=impediment_description, responsible=responsible, user_id=current_user.id)
            db.session.add(new_impediment)
            db.session.commit()

            respuesta_html = markdown.markdown(f"**Impedimento '{impediment_description}' registrado. Responsable: '{responsible}'.**")
            session['chatbot_state'] = {'action': None, 'data': {}} # Reinicia el estado

        elif pregunta.lower().startswith("agregar tarea:"):
            task_name = pregunta[len("agregar tarea:"):].strip()
            if task_name:
                session['chatbot_state'] = {'action': 'add_task_details', 'data': {'task_name': task_name}}
                respuesta_html = markdown.markdown(f"Perfecto, voy a agregar la tarea: **{task_name}**. ¿Deseas añadir más detalles como estimación, prioridad, o descripción? (Ej: 'Prioridad alta, 3 horas')")
            else:
                respuesta_html = markdown.markdown("Por favor, especifica el nombre de la tarea. Ejemplo: `Agregar tarea: Configurar base de datos`")

        elif pregunta.lower().startswith("registrar impedimento:"):
            impediment_description = pregunta[len("registrar impedimento:"):].strip()
            if impediment_description:
                session['chatbot_state'] = {'action': 'add_impediment_responsible', 'data': {'impediment_description': impediment_description}}
                respuesta_html = markdown.markdown(f"Entendido. **'{impediment_description}'**. ¿Quién es el responsable de resolver este impedimento?")
            else:
                respuesta_html = markdown.markdown("Por favor, describe el impedimento. Ejemplo: `Registrar impedimento: Servidor caído`")
        
        # Las funcionalidades "ver tareas" y "ver impedimentos" se eliminan del chat aquí.
        # Ahora se accede a ellas directamente desde la barra lateral.
        # Esto es clave para que sean páginas separadas.
        # La IA ya no responderá a estos comandos en el chat.
        # elif pregunta.lower() == "ver tareas":
        #    return redirect(url_for('listar_tareas')) # Redirige a la nueva página de tareas
        # elif pregunta.lower() == "ver impedimentos":
        #    return redirect(url_for('listar_impedimentos')) # Redirige a la nueva página de impedimentos
        
        else:
            # --- Envío a la API de Llama para preguntas generales de Scrum ---
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
                    respuesta_html = markdown.markdown(respuesta_markdown)
                else:
                    respuesta_html = "No pude obtener una respuesta del modelo en este momento."
            except Exception as e:
                respuesta_html = f"Ocurrió un error al contactar al experto en Scrum: {e}"
            
            session['chatbot_state'] = {'action': None, 'data': {}} # Reinicia el estado si es una pregunta normal

    return render_template("index.html", respuesta=respuesta_html, 
                           show_login_modal=show_login_modal, show_register_modal=show_register_modal,
                           messages=messages, current_user=current_user)

if __name__ == "__main__":
    with app.app_context():
        db.create_all() # Crea las tablas de la base de datos si no existen
    app.run(debug=True)