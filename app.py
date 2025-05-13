from flask import Flask, request, render_template
from PIL import Image
import pytesseract
import os
import pyodbc

app = Flask(__name__)

pytesseract.pytesseract.tesseract_cmd = r'C:\\Program Files\\Tesseract-OCR\\tesseract.exe'


server = r'localhost\SQLEXPRESS'
database = 'OCR_DB'

connection_string = f'''
    DRIVER={{ODBC Driver 17 for SQL Server}};
    SERVER={server};
    DATABASE={database};
    Trusted_Connection=yes;
'''

@app.route('/')
def upload_form():
    receipts = get_receipts()
    return render_template('upload.html', receipts=receipts)

@app.route('/upload', methods=['POST'])
def upload_image():
    if 'file' not in request.files:
        return 'No file part'
    file = request.files['file']
    if file.filename == '':
        return 'No selected file'
    if file:
        image_path = os.path.join('static', file.filename)
        file.save(image_path)

        pytesseract.pytesseract.tesseract_cmd = "C:\\Program Files\\Tesseract-OCR\\tesseract.exe"

        text = pytesseract.image_to_string(Image.open(image_path))

        receipt_data = extract_receipt_data(text)


        return render_template('result.html', data=receipt_data)
#puppeteer-core

def extract_receipt_data(text):
    lines = text.split('\n')
    receipt_info = {}
    
    for line in lines:
        if "total" in line.lower():
            receipt_info['Total'] = line.replace('Total','').replace(':','').strip()
        if "date" in line.lower():
            receipt_info['Date'] = line.replace('Date','').replace(':','').strip()
        if "receipt number" in line.lower() or "receipt no" in line.lower():
            receipt_info['receipt number'] = line.replace('Receipt Number','').replace('Receipt No','').replace(':','').strip()
        if "name" in line.lower() or "prepared for" in line.lower():
            receipt_info['Name'] = line.replace('Name','').replace('Prepared for','').replace('Patient Name','').replace(':','').strip()

    insert_receipt(receipt_info['Name'], receipt_info['Date'], receipt_info['Total'], receipt_info['receipt number'])

    return receipt_info

def insert_receipt(name, date, total, Receipt_number):

    conn = pyodbc.connect(connection_string)
    cursor = conn.cursor()

    cursor.execute('''
    INSERT INTO receipts (ReceiptNumber, Name, Date, Total)
    VALUES (?, ?, ?, ?)
    ''', (Receipt_number, name, date, total))
    
    conn.commit()

    cursor.close()
    conn.close()

def get_receipts():
    conn = pyodbc.connect(connection_string)
    cursor = conn.cursor()
    
    cursor.execute('SELECT * FROM receipts')
    records = cursor.fetchall()

    cursor.close()
    conn.close()

    return records

if __name__ == '__main__':
    app.run(port=5000)
