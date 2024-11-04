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

df = pd.read_excel(excel_path)
valores_columna_b = df['B'].tolist()

pdf_reader = PdfReader(pdf_path)
pdf_writer = PdfWriter()

pdfmetrics.registerFont(TTFont('Roboto', roboto_font_path))
pdfmetrics.registerFont(TTFont('Roboto-Black', roboto_black_font_path))

def obtener_ubicacion_nombre(page_text, patron_nombre):
    matches = list(re.finditer(patron_nombre, page_text))
    if matches:
        for match in matches:
            nombre = match.group()
            print(f"Nombre encontrado: {nombre} en la posición {match.start()}-{match.end()}")

for page_num in range(len(pdf_reader.pages)):
    page = pdf_reader.pages[page_num]
    page_text = page.extract_text()
    if page_text:
        patron_nombre = r"[A-ZÁÉÍÓÚÑ][a-záéíóúñ]+,[A-ZÁÉÍÓÚÑ][a-záéíóúñ]+(?:[a-záéíóúñ]*)"
        obtener_ubicacion_nombre(page_text, patron_nombre)

def agregar_texto_a_pdf(page, page_num, texto, texto_en_palabras, ultima_pagina=False):
    packet = io.BytesIO()
    can = canvas.Canvas(packet, pagesize=letter)
    can.setFont("Roboto-Black", 10)
    
    if ultima_pagina:
        x, y = 135, 300
        can.drawString(x, y, f"{texto}")
        x_palabras, y_palabras = 80, 510  # Mover las palabras más a la izquierda
    else:
        x, y = 135, 267
        can.drawString(x, y, f"{texto}")
        x_palabras, y_palabras = 100, 475  # Mover las palabras más a la izquierda
        
    can.setFont("Roboto", 10)
    can.drawString(x_palabras, y_palabras, f"{texto_en_palabras}")
    can.save()

    packet.seek(0)
    new_pdf = PdfReader(packet)
    page.merge_page(new_pdf.pages[0])
    pdf_writer.add_page(page)

for page_num in range(len(pdf_reader.pages)):
    page = pdf_reader.pages[page_num]
    ultima_pagina = (page_num == len(pdf_reader.pages) - 1)
    
    if page_num < len(valores_columna_b):
        valor = valores_columna_b[page_num]
        texto_reemplazo = f"{valor:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")
        parte_entera = int(valor)
        centavos = int(round((valor - parte_entera) * 100))
        texto_reemplazo_en_palabras = f"{num2words(parte_entera, lang='es').capitalize()} con {centavos:02d}/100 centavos"
        
        agregar_texto_a_pdf(page, page_num, texto_reemplazo, texto_reemplazo_en_palabras, ultima_pagina=ultima_pagina)
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
            fileId=file_id,
            body=user_permission,
            fields='id'
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
