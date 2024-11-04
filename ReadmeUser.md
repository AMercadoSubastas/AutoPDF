
# Manual de Usuario para AutoPDF

Este manual describe paso a paso el uso del script **AutoPDF**, el cual descarga archivos desde Google Drive, modifica un archivo PDF agregando valores y texto basado en los datos de un archivo Excel, y luego sube el archivo modificado de nuevo a Google Drive, compartiéndolo con un usuario específico. A continuación, se detallan los pasos para configurar y ejecutar este proceso.

## Requisitos previos

* **Python 3.7+**: Este script está desarrollado en Python y requiere al menos la versión 3.7 o superior.
* **Docker**: Se proporciona un archivo Docker para la configuración del entorno necesario. Debes tener Docker instalado.
* **Credenciales de Google Cloud**: Necesitas un archivo de credenciales `<span>service_account.json</span>` para poder acceder a Google Drive desde la cuenta de servicio.
* **Paquetes Python**: Se usan varias bibliotecas de Python, tales como `<span>pandas</span>`, `<span>PyPDF2</span>`, `<span>reportlab</span>`, y `<span>google-api-python-client</span>`. El contenedor Docker se encarga de instalarlas.

## Configuración del Proyecto

### Obtener Credenciales de Google Cloud

1. Dirígete a [Google Cloud Console](https://console.developers.google.com/).
2. Crea un proyecto nuevo o utiliza uno existente.
3. Ve a la sección **APIs y Servicios** y habilita la API de Google Drive.
4. Crea una cuenta de servicio y descarga el archivo de credenciales JSON (`<span>service_account.json</span>`).
5. Comparte los archivos requeridos en Google Drive con la cuenta de correo electrónico del servicio (`<span>client_email</span>` en el archivo de credenciales).

### Colocar Credenciales

* Coloca el archivo `<span>service_account.json</span>` en el mismo directorio donde está el script.

## Ejecución del Contenedor Docker

El contenedor Docker te proporciona un entorno listo para ejecutar el script sin necesidad de instalar los paquetes manualmente.

### Construir la Imagen Docker

1. En la terminal, navega hasta el directorio del proyecto.
2. Construye la imagen con:
   ```
   docker build -t autopdf .
   ```

### Ejecutar el Contenedor Docker

* Una vez construida la imagen, ejecuta el contenedor con el siguiente comando:

  ```
  docker run --rm -v "$(pwd)/output:/app/output" autopdf
  ```

  * El comando anterior monta un volumen para que puedas acceder al archivo PDF generado en tu sistema local, dentro de la carpeta `<span>output</span>`.

## Detalle del Script

### Descargar Archivos desde Google Drive

* El script se conecta a Google Drive usando las credenciales proporcionadas y descarga los archivos PDF y Excel especificados.
* Los IDs de los archivos (`<span>pdf_file_id</span>` y `<span>excel_file_id</span>`) deben ser ajustados según los archivos que deseas utilizar. Puedes buscar estos IDs ejecutando una consulta de listado con la API de Google Drive, como se muestra al inicio del script.

### Modificación del PDF

* Se utiliza **PyPDF2** para leer el archivo PDF original y **ReportLab** para agregar texto sobre él.
* Los valores para agregar provienen del archivo Excel descargado.
* Se utiliza una fuente llamada **Roboto-Black** para los valores numéricos y **Roboto** para los textos descriptivos en palabras. Asegúrate de tener estos archivos de fuentes (`<span>Roboto-Regular.ttf</span>` y `<span>Roboto-Black.ttf</span>`) en la carpeta `<span>Roboto/</span>` dentro del directorio del proyecto.

### Subida y Compartición del PDF Generado

* Una vez modificado el PDF, se sube de nuevo a Google Drive.
* El script comparte el archivo generado con un correo electrónico especificado, asignándole permisos de escritura.

### Limpieza de Archivos Locales

* Tras la generación del PDF, el script elimina los archivos descargados y el archivo PDF actualizado de la carpeta local, para mantener limpio el entorno.

## Ejemplo de Ejecución

### Configura los IDs de los Archivos

* Busca los archivos en tu Google Drive y copia sus IDs.
* Coloca esos IDs en las variables `<span>pdf_file_id</span>` y `<span>excel_file_id</span>` dentro del script.

### Ejecuta el Contenedor Docker

* Después de construir la imagen Docker como se mencionó anteriormente, corre el script para generar el PDF actualizado.

### Revisa Google Drive

* El archivo actualizado será subido a Google Drive y compartido con el correo especificado (`<span>lvargas@grupoadrianmercado.com</span>` en este ejemplo).

## Notas Finales

* Asegúrate de que el correo del servicio de Google tenga permisos de lectura en los archivos originales que deseas descargar.
* Si necesitas cambiar el formato del archivo Excel o PDF, modifica el script según corresponda.
* Los textos agregados en el PDF están posicionados de manera que se puedan ajustar a documentos de tamaño **letter**.
