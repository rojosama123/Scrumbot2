import React, { useState, useRef, useEffect } from "react";
import "./App.css";

function App() {
  const [mensaje, setMensaje] = useState("");
  const [conversacion, setConversacion] = useState([]);
  const [cargando, setCargando] = useState(false);
  const chatRef = useRef(null);

  const enviarPregunta = async () => {
    if (!mensaje.trim()) return;

    const nuevaConversacion = [...conversacion, { rol: "usuario", texto: mensaje }];
    setConversacion(nuevaConversacion);
    setMensaje("");
    setCargando(true);

    try {
      const res = await fetch("http://localhost:8000/chat", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ mensaje }),
      });

      const data = await res.json();
      setConversacion([...nuevaConversacion, { rol: "bot", texto: data.respuesta }]);
    } catch (error) {
      setConversacion([...nuevaConversacion, { rol: "bot", texto: "Error al conectar con el backend." }]);
    } finally {
      setCargando(false);
    }
  };

  useEffect(() => {
    chatRef.current?.scrollTo(0, chatRef.current.scrollHeight);
  }, [conversacion]);

  return (
    <div className="container">
      <h1>🤖 ScrumBot</h1>
      <div className="chat-box" ref={chatRef}>
        {conversacion.map((msg, i) => (
          <div key={i} className={`mensaje ${msg.rol}`}>
            <div className="burbuja">{msg.texto}</div>
          </div>
        ))}
        {cargando && <div className="mensaje bot"><div className="burbuja">Escribiendo...</div></div>}
      </div>
      <div className="input-box">
        <textarea
          value={mensaje}
          onChange={(e) => setMensaje(e.target.value)}
          placeholder="Escribe tu pregunta sobre Scrum..."
        />
        <button onClick={enviarPregunta} disabled={cargando || !mensaje.trim()}>
          Enviar
        </button>
      </div>
    </div>
  );
}

export default App;
