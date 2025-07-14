#!/bin/sh

echo "Inicializando la base de datos..."
python /app/init_db.py # Ahora llama al script en vez de la cadena

echo "Base de datos inicializada. Iniciando la aplicación Flask..."
exec "$@"