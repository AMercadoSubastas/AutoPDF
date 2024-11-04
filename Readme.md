# AutoPDF - Script Dockerizado para Integración de PDF y Google Drive

## Descripción General

El script `AutoPDF `automatiza el proceso de descargar archivos desde Google Drive, modificar un archivo PDF agregando datos de un archivo Excel, y luego subir el PDF modificado de vuelta a Google Drive. Todo este proceso está containerizado usando Docker, lo que facilita la configuración, ejecución y despliegue.

Esta guía proporciona instrucciones paso a paso para configurar el entorno, establecer las credenciales de Google y construir y ejecutar el contenedor Docker.

## Prerrequisitos

* Docker instalado en tu sistema.
* Cuenta de Google Cloud Platform para crear una cuenta de servicio.
* Dependencias de Python para trabajar con las APIs de Google, manipulación de PDF y procesamiento de datos.

## Instrucciones de Configuración

### Paso 1: Configurar Credenciales de la Cuenta de Servicio de Google Cloud

1. **Crear un Proyecto en Google Cloud**
   * Ve a [Google Cloud Console](https://console.cloud.google.com/).
   * Crea un nuevo proyecto o selecciona uno existente.
2. **Habilitar la API de Google Drive**
   * Ve a la [Biblioteca de APIs de Google](https://console.developers.google.com/apis/library).
   * Busca "Google Drive API" y habilítala para tu proyecto.
3. **Crear una Cuenta de Servicio**
   * Navega a la [página de Cuentas de Servicio](https://console.cloud.google.com/iam-admin/serviceaccounts).
   * Haz clic en **Crear Cuenta de Servicio** y proporciona un nombre para ella.
   * Otorga a la cuenta de servicio el rol de **Editor** o **Viewer** para el acceso a Google Drive.
   * Después de crear la cuenta de servicio, genera una clave en formato JSON. Esta clave se utilizará para la autenticación.
   * Descarga el archivo de clave JSON y guárdalo como `service_account.json` en el directorio raíz del proyecto.
4. **Compartir Archivos de Google Drive**
   * Ve a Google Drive y comparte los archivos que deseas acceder con la dirección de correo electrónico de tu cuenta de servicio (`client_email `en el archivo `service_account.json`). Este paso asegura que la cuenta de servicio tenga los permisos adecuados para acceder a los archivos.
5. **Obtener los IDs de los Archivos en Google Drive**
   * Navega a Google Drive y selecciona los archivos PDF y Excel que deseas utilizar.
   * Haz clic derecho en cada archivo y selecciona **Obtener enlace**. Copia la URL del enlace.
   * El ID del archivo es la parte de la URL que sigue a `/d/` y termina antes de `/edit`. Por ejemplo, en la URL `https://drive.google.com/file/d/1X4yHlic86Pb8-wRpCXd4vz9m89ELaO9s/edit,` el ID del archivo es `1X4yHlic86Pb8-wRpCXd4vz9m89ELaO9s`
   * Utiliza estos IDs para configurar las variables `pdf_file_id`y `excel_file_id` en el script.

### Paso 2: Preparar los Archivos del Proyecto

Asegúrate de tener los siguientes archivos y directorios en la carpeta de tu proyecto:

1. `AutoPDF.py`: El script principal que automatiza todo el proceso.
2. `service_account.json`: Archivo de credenciales para la cuenta de servicio de Google Cloud.
3. `Roboto`: Directorio que contiene el archivo de fuente `<span>Roboto-Regular.ttf</span>` usado por el script.
4. `Dockerfile`: Archivo de configuración de Docker para construir el contenedor.

### Paso 3: Configuración del Dockerfile

El `Dockerfile` ya está preparado para crear una imagen Docker que contiene todas las dependencias necesarias y configuraciones del entorno para ejecutar el script `AutoPDF.py`

Aquí está el `Dockerfile` utilizado:

```
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

# Instalar las dependencias necesarias
RUN apt-get update && \
    apt-get install -y gcc libffi-dev libssl-dev && \
    pip install --no-cache-dir pandas PyPDF2 reportlab google-api-python-client google-auth google-auth-oauthlib google-auth-httplib2 num2words

# Ejecutar el script Python
CMD ["python3", "AutoPDF.py"]
```

### Paso 4: Construir la Imagen Docker

Para construir la imagen Docker, ejecuta el siguiente comando en la terminal:

```
docker build -t autopdf .
```

Este comando crea una imagen llamada `autopdf` con todas las configuraciones necesarias.

### Paso 5: Ejecutar el Contenedor Docker

Para ejecutar el contenedor y ejecutar el script, usa el siguiente comando:

```
docker run --rm -v "$(pwd)/output:/app/output" autopdf
```

* `<span><strong>--rm</strong></span>`: Elimina el contenedor después de que el script haya terminado de ejecutarse.
* `<span><strong>-v "$(pwd)/output:/app/output"</strong></span>`: Monta un volumen para que los archivos de salida sean accesibles fuera del contenedor. El PDF modificado se guardará en una carpeta `<span>output</span>`.

### Paso 6: Flujo de Trabajo del Script

1. **Descargar Archivos de Google Drive**
   * El script descarga un archivo PDF y un archivo Excel especificados desde Google Drive.
2. **Modificar el PDF**
   * El archivo Excel se lee utilizando `pandas` para extraer valores.
   * El PDF se modifica utilizando `PyPDF2` y `reportlab` para agregar información basada en los valores del archivo Excel.
3. **Guardar y Subir el PDF Modificado**
   * El PDF modificado se guarda localmente y luego se sube de nuevo a Google Drive.
   * El archivo subido se comparte con el usuario especificado.
4. **Eliminar Archivos Locales**
   * Después de subir el PDF, los archivos locales se eliminan para mantener el entorno limpio.

### Explicación del Código del Script

* **Importar Dependencias**: Se importan módulos como `os`, `pandas`, `PyPDF2,` `reportlab`, y módulos de Google para manejar Drive y las credenciales.
* **Credenciales de Google Drive**: Se cargan las credenciales de `service_account.json` y se crea un cliente `service`para Google Drive.
* **Descargar Archivos**: La función `descargar_archivo_drive()` se encarga de descargar los archivos PDF y Excel desde Google Drive.
* **Modificar PDF**: Se usa `pandas` para leer datos del Excel y `reportlab` para escribir texto adicional en el PDF. La modificación se realiza página por página.
* **Guardar y Subir PDF**: El PDF modificado se guarda localmente, luego se sube a Google Drive usando `subir_y_compartir_archivo_drive()`. Después se comparte con un correo electrónico especificado.
* **Limpieza**: Se eliminan los archivos locales descargados y el PDF generado después de completar las tareas.

## Notas Adicionales

* **Compartir Archivos de Google Drive**: Asegúrate de que los archivos en Google Drive estén compartidos con el correo electrónico de la cuenta de servicio para el acceso y modificación exitosa.
* **Obtener IDs de Archivos**: Para obtener los IDs de los archivos que deseas usar en el script, navega a Google Drive, selecciona los archivos y copia la parte relevante de la URL, como se explicó en el Paso 1.5.
* **Variables de Entorno**: Puedes agregar variables de entorno para información sensible como credenciales si prefieres no incluirlas directamente en el código.

## Problemas Comunes

1. **Problemas de Autenticación**: Asegúrate de que tu archivo `service_account.json` sea correcto y contenga todos los campos necesarios, incluyendo `client_email`, `private_key`, y `token_uri`
2. **Archivo No Encontrado (Google Drive)**: Asegúrate de que los IDs de archivo sean correctos y de que la cuenta de servicio tenga permisos de acceso.
3. **Permisos de Docker**: Asegúrate de que Docker tenga permisos para leer/escribir archivos en el directorio actual.


### Explicación del Archivo .env

El archivo `.env` se utiliza para almacenar configuraciones sensibles y variables de entorno que el script `AutoPDF.py` necesita para funcionar correctamente. Esto ayuda a mantener el código más seguro y organizado al no tener información crítica escrita directamente en el script. Aquí está el desglose de las variables:

1. **SCOPES** : Define el ámbito de acceso para la API de Google Drive. En este caso, se establece como `https://www.googleapis.com/auth/drive`, lo que permite el acceso completo a los archivos en Google Drive.
2. **SERVICE_ACCOUNT_FILE** : La ruta al archivo JSON de la cuenta de servicio de Google Cloud, que contiene las credenciales necesarias para la autenticación.
3. **PDF_FILE_ID** : El ID del archivo PDF en Google Drive que se descargará y modificará. Se obtiene a partir de la URL del archivo en Google Drive.
4. **EXCEL_FILE_ID** : El ID del archivo Excel en Google Drive que se usará para extraer los datos. También se obtiene desde la URL del archivo en Google Drive.
5. **ROBOTO_FONT_PATH** : La ruta al archivo de la fuente `Roboto-Regular.ttf`, que se usa para agregar texto al PDF modificado.
6. **ROBOTO_BLACK_FONT_PATH** : La ruta al archivo de la fuente `Roboto-Black.ttf`, utilizada para resaltar el texto en el PDF.
7. **USER_EMAIL** : El correo electrónico con el que se compartirá el archivo PDF modificado en Google Drive.

Este archivo debe mantenerse seguro y no compartirse públicamente, ya que contiene información confidencial, como las credenciales de la cuenta de servicio y el correo electrónico del usuario.

## Conclusión

Esta guía te ha guiado a través de todo el proceso de configuración y ejecución del script `AutoPDF` utilizando Docker. Al containerizar el script, aseguras la consistencia a través de diferentes entornos, facilitando su despliegue y compartición con otros.

No dudes en comunicarte si encuentras algún problema o tienes preguntas sobre la configuración.
