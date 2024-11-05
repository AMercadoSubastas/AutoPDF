#!/bin/bash
# Cambiar al directorio donde está el proyecto (ajusta la ruta según sea necesario)
cd "$(dirname "$0")"

# Construir la imagen de Docker (solo la primera vez o cuando se hagan cambios)
docker build -t autopdf .

# Ejecutar el contenedor de Docker
docker run --rm -v "$PWD":/app autopdf
