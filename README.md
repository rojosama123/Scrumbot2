## Para levantar el ScrumBot hagan lo siguiente en una termina abierta en la carpeta raiz del proyecto (o en el mismo visual):

1. docker login (se logueando con su cuenta de docker)
2. docker-compose up --build -d (levantan el contenedor en segundo plano)
3. docker-compose down (tiran abajo el contenedor)

## Si realizan cambios en cualquier archivo del proyecto tiene que hacer el punto 3 y luego el 2. Esto es porque tiene que construir de nuevo la imagen y el contenedor.

## Para ver la base de datos (dentro de una terminal igual):

1. docker cp chatbot-scrum:/app/instance/site.db ./site.db

Esta linea les copiará y pegará el archivo site.db en el proyecto y ahí pueden ver las tablas de la base de datos.