# Utilizar una imagen base de Python 3.12
FROM python:3.12-slim

# Establecer el directorio de trabajo en el contenedor
WORKDIR /app

# Copiar el archivo service_account.json al contenedor
COPY service_account.json /app/

# Copiar la carpeta Roboto (fuente) al contenedor
COPY Roboto /app/Roboto

# Copiar el script Python al contenedor
COPY AutoPDF.py /app/

# Copiar el archivo .env al contenedor
COPY .env /app/

# Instalar las dependencias necesarias
RUN apt-get update && \
    apt-get install -y gcc libffi-dev libssl-dev && \
    pip install --no-cache-dir pandas PyPDF2 reportlab google-api-python-client google-auth google-auth-oauthlib google-auth-httplib2 num2words openpyxl python-dotenv

# Ejecutar el script Python
CMD ["python3", "AutoPDF.py"]
