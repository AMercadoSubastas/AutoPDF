import os
from dotenv import load_dotenv
import pandas as pd
from PyPDF2 import PdfReader, PdfWriter
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import letter
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
import io
from num2words import num2words
import re
from datetime import datetime
from google.oauth2 import service_account
from googleapiclient.discovery import build
from googleapiclient.http import MediaIoBaseDownload, MediaFileUpload
from googleapiclient.errors import HttpError

# Cargar variables del archivo .env
load_dotenv()

# Variables cargadas desde el archivo .env
SCOPES = [os.getenv('SCOPES')]
service_account_file = os.getenv('SERVICE_ACCOUNT_FILE')
pdf_file_id = os.getenv('PDF_FILE_ID')
excel_file_id = os.getenv('EXCEL_FILE_ID')
roboto_font_path = os.getenv('ROBOTO_FONT_PATH')
roboto_black_font_path = os.getenv('ROBOTO_BLACK_FONT_PATH')
user_email = os.getenv('USER_EMAIL')

credentials = service_account.Credentials.from_service_account_file(
    service_account_file, scopes=SCOPES)

try:
    service = build('drive', 'v3', credentials=credentials)
    results = service.files().list(pageSize=10, fields="files(id, name)").execute()
    items = results.get('files', [])

    if not items:
        print("No se encontraron archivos en Google Drive.")
    else:
        print("Conexión exitosa a Google Drive. Archivos encontrados:")
        for item in items:
            print(f"{item['name']} (ID: {item['id']})")
except Exception as e:
    print("Error al conectar con Google Drive:", e)
    exit(1)

def descargar_archivo_drive(file_id, nombre_destino, mime_type=None):
    if mime_type:
        request = service.files().export_media(fileId=file_id, mimeType=mime_type)
    else:
        request = service.files().get_media(fileId=file_id)
    
    fh = io.FileIO(nombre_destino, 'wb')
    downloader = MediaIoBaseDownload(fh, request)

    done = False
    while not done:
        status, done = downloader.next_chunk()
        print(f"Descargando {nombre_destino}: {int(status.progress() * 100)}% completado.")

pdf_path = 'recmanuales.ok.fake.pdf'
excel_path = 'recmanuales.ok.fakeHC.xlsx'

descargar_archivo_drive(pdf_file_id, pdf_path)
descargar_archivo_drive(excel_file_id, excel_path)

mes_actual = datetime.now().strftime("%B").capitalize()
output_pdf_path = f'recmanuales_{mes_actual}.pdf'

# Cargar el archivo Excel y las columnas relevantes
df = pd.read_excel(excel_path)
nombres_excel = df['Nombre Completo'].tolist()
print(nombres_excel)
valores_columna_b = df['B'].tolist()

# Crear un diccionario para relacionar nombres con valores
nombre_valor_dict = dict(zip(nombres_excel, valores_columna_b))

pdf_reader = PdfReader(pdf_path)
pdf_writer = PdfWriter()

pdfmetrics.registerFont(TTFont('Roboto', roboto_font_path))
pdfmetrics.registerFont(TTFont('Roboto-Black', roboto_black_font_path))

def extraer_nombres_con_espacios(page_text):
    # Actualizar la expresión regular para incluir caracteres acentuados
    patron = r"A\s*C\s*L\s*A\s*R\s*A\s*C\s*I\s*Ó\s*N\s*:\s*([\w\sÁÉÍÓÚÑáéíóúñ,]+)\s*D\s*N\s*I"
    matches = re.findall(patron, page_text)
    nombres_formateados = []
    
    if matches:
        for nombre in matches:
            # Limpiar los espacios extra y dividir en partes
            nombre_limpio = ''.join(nombre.split())
            partes = nombre_limpio.split(',')
            if len(partes) == 2:
                apellido = partes[0].strip()
                nombre_completo = ' '.join(partes[1].split())
                
                # Insertar espacio entre mayúsculas consecutivas que no tienen espacio
                apellido = re.sub(r'(?<=[a-záéíóúñ])(?=[A-ZÁÉÍÓÚÑ][a-záéíóúñ])', ' ', apellido)
                
                # Insertar espacio entre una letra minúscula seguida de una letra mayúscula
                nombre_completo = re.sub(r'(?<=[a-záéíóúñ])(?=[A-ZÁÉÍÓÚÑ])', ' ', nombre_completo)
                
                nombres_formateados.append(f"{apellido}, {nombre_completo}")
    
    return nombres_formateados

# Contar cuántas veces aparece la palabra "pesos" en el PDF
conteo_palabra_pesos = 0
nombres_en_paginas = {}

for page_num in range(len(pdf_reader.pages)):
    page = pdf_reader.pages[page_num]
    page_text = page.extract_text()
    if page_text:
        conteo_palabra_pesos += page_text.lower().count("p e s o s")
        nombres = extraer_nombres_con_espacios(page_text)
        if nombres:
            nombres_en_paginas[f"Página {page_num + 1}"] = nombres

print(f"La palabra 'pesos' aparece {conteo_palabra_pesos} veces en el PDF.")
for pagina, nombres in nombres_en_paginas.items():
    for nombre in nombres:
        # Imprimir los nombres para ver exactamente cómo se comparan
        print(f"Nombre extraído: '{nombre}'")
        
        if nombre in nombre_valor_dict:
            valor = nombre_valor_dict[nombre]
            print(f"{pagina}: {nombre} - Valor: {valor}")
        else:
            # Si el nombre no se encuentra, imprimir un mensaje de depuración
            print(f"Nombre no encontrado en el Excel: '{nombre}'")

def agregar_texto_a_pdf(page, texto, texto_en_palabras, ultima_pagina=False):
    packet = io.BytesIO()
    can = canvas.Canvas(packet, pagesize=letter)
    can.setFont("Roboto-Black", 10)
    
    # Ajustar las coordenadas según si es la última página o no
    if ultima_pagina:
        x, y = 135, 300
        x_palabras, y_palabras = 85, 510  # Mover las palabras más a la izquierda
    else:
        x, y = 135, 267
        x_palabras, y_palabras = 85, 475   # Mover las palabras más a la izquierda
    
    can.drawString(x, y, f"{texto}")
    can.setFont("Roboto", 10)
    
    palabras = texto_en_palabras.split()
    
    if len(palabras) >= 11:
        primera_linea = " ".join(palabras[:11])
        segunda_linea = " ".join(palabras[11:])
        can.drawString(x_palabras, y_palabras, primera_linea)
        can.drawString(x_palabras, y_palabras - 36, segunda_linea)  # Mover la segunda línea hacia abajo
    else:
        can.drawString(x_palabras, y_palabras, texto_en_palabras)

    can.save()
    packet.seek(0)
    new_pdf = PdfReader(packet)
    page.merge_page(new_pdf.pages[0])
    pdf_writer.add_page(page)

# Iterar sobre las páginas y nombres, y agregar el texto al PDF
for page_num in range(len(pdf_reader.pages)):
    page = pdf_reader.pages[page_num]
    ultima_pagina = (page_num == len(pdf_reader.pages) - 1)
    nombres = nombres_en_paginas.get(f"Página {page_num + 1}", [])
    
    if nombres:
        for nombre in nombres:
            if nombre in nombre_valor_dict:
                valor = nombre_valor_dict[nombre]
                texto_reemplazo = f"{valor:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")
                parte_entera = int(valor)
                centavos = int(round((valor - parte_entera) * 100))
                texto_reemplazo_en_palabras = f"{num2words(parte_entera, lang='es').capitalize()} con {centavos:02d}/100 centavos"
                agregar_texto_a_pdf(page, texto_reemplazo, texto_reemplazo_en_palabras, ultima_pagina=ultima_pagina)
    else:
        pdf_writer.add_page(page)

with open(output_pdf_path, 'wb') as output_pdf:
    pdf_writer.write(output_pdf)

print(f"PDF actualizado guardado como: {output_pdf_path}")

try:
    os.remove(pdf_path)
    os.remove(excel_path)
    print("Archivos descargados eliminados exitosamente.")
except Exception as e:
    print(f"Error al eliminar archivos locales: {e}")

def subir_y_compartir_archivo_drive(nombre_archivo, nombre_drive, user_email):
    file_metadata = {'name': nombre_drive}
    media = MediaFileUpload(nombre_archivo, mimetype='application/pdf')
    try:
        file = service.files().create(body=file_metadata, media_body=media, fields='id').execute()
        file_id = file.get('id')
        print(f"Archivo subido exitosamente: {nombre_drive} (ID: {file_id})")
        compartir_archivo_drive(file_id, user_email)
    except Exception as e:
        print(f"Error al subir archivo a Google Drive: {e}")

def compartir_archivo_drive(file_id, user_email):
    try:
        user_permission = {
            'type': 'user',
            'role': 'writer',
            'emailAddress': user_email
        }
        service.permissions().create(
            fileId=file_id, body=user_permission, fields='id'
        ).execute()
        print(f"Archivo compartido exitosamente con {user_email}")
    except HttpError as error:
        print(f"Error al compartir archivo: {error}")

subir_y_compartir_archivo_drive(output_pdf_path, f'recmanuales_actualizado_{mes_actual}.pdf', user_email)

try:
    os.remove(output_pdf_path)
    print("Archivo PDF actualizado eliminado exitosamente.")
except Exception as e:
    print(f"Error al eliminar el archivo PDF actualizado: {e}")
