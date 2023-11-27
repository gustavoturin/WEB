from flask import Flask, render_template, request
import pandas as pd
from exchangelib import Credentials, Account, Message, HTMLBody, FileAttachment
import os
import csv
import xml.etree.ElementTree as ET
import logging
from werkzeug.utils import secure_filename

UPLOAD_FOLDER = r"F:\Cartas\Gustavo Alves"
ALLOWED_EXTENSIONS = {'csv'}

app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

# Configuração básica de logging
logging.basicConfig(filename='error.log', level=logging.ERROR)

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        try:
            # Verifica se o arquivo foi enviado com a solicitação
            if 'file' not in request.files:
                return render_template('error.html', error="No file part")

            file = request.files['file']

            # Verifica se o nome do arquivo está vazio
            if file.filename == '':
                return render_template('error.html', error="No selected file")

            # Verifica se o arquivo tem uma extensão válida
            if file and allowed_file(file.filename):
                # Salva o arquivo no caminho de upload
                filename = secure_filename(file.filename)
                file_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
                file.save(file_path)

                # Realiza operações com base no arquivo enviado
                # ...

                return render_template('success.html')

            else:
                return render_template('error.html', error="Invalid file extension")

        except Exception as e:
            error_message = f"An unexpected error occurred: {e}"
            logging.error(error_message)
            return render_template('error.html', error="An unexpected error occurred. Please contact support.")

    return render_template('index.html')

def csv_to_xml(csv_file_path):
    csv_directory = os.path.dirname(csv_file_path)

    with open(csv_file_path, 'r', encoding='latin-1') as csv_file:
        csv_reader = csv.DictReader(csv_file, delimiter=';')
        
        root = ET.Element('data')

        for row in csv_reader:
            entry = ET.SubElement(root, 'entry')
            for field, value in row.items():
                field_elem = ET.SubElement(entry, field)
                field_elem.text = value

        xml_file_path = os.path.join(csv_directory, 'nf.xml')

        tree = ET.ElementTree(root)

        tree.write(xml_file_path, encoding='utf-8', xml_declaration=True)
        
        return xml_file_path

def enviar_email(xml_file_path):
    email = 'roborfaa@outlook.com'
    senha_app_especifica = 'Rf@@1234'

    credentials = Credentials(email, senha_app_especifica)

    account = Account(email, credentials=credentials, autodiscover=True)

    subject = 'Arquivo convertido'
    body = 'Segue em anexo o arquivo (xml)'
    to_email = 'galves@rfaa.com.br'

    message = Message(
        account=account,
        folder=account.sent,
        subject=subject,
        body=HTMLBody(body),
        to_recipients=[to_email]
    )

    with open(xml_file_path, 'rb') as file:
        xml_attachment = FileAttachment(name='nf.xml', content=file.read())
        message.attach(xml_attachment)

    message.send()

    os.remove(xml_file_path)
    csv_file_path = os.path.splitext(xml_file_path)[0] + '.csv'
    os.remove(csv_file_path)

if __name__ == '__main__':
    app.run(debug=True)
