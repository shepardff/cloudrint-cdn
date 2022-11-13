from flask import Flask, request
from flask_restful import Resource, Api
import uuid
import os
from PIL import Image
import base64
import sqlite3
from flask_cors import CORS
from pathlib import Path


Path("images/previews").mkdir(parents=True, exist_ok=True)
Path("images/uploads").mkdir(parents=True, exist_ok=True)

app = Flask(__name__)
CORS(app)
api = Api(app)

@app.route('/', methods=['GET'])
def hello():
    return {'hello': True}

@app.route('/order', methods=['POST'])
def order():
    conn = sqlite3.connect('database.db')
    # conn.execute('CREATE TABLE students (name TEXT, addr TEXT, city TEXT, pin TEXT)')
    conn.close()
    # Все данные формы отправляем на почту и запускаем очередь на генерацию архива
    # + сохраняются все фото и данные формы в таблицы
    # Генерация архива проходит в js файле
    phone = request.form.get('phone')
    return {'success': True}

@app.route('/file', methods=['POST'])
def upload():
    file = request.files['file']
    file_ext = os.path.splitext(file.filename)[1]
    file_id = str(uuid.uuid1()) + str(uuid.uuid1())
    filename = file_id + str(file_ext)
    preview_path = 'images/previews/' + filename
    upload_path = 'images/uploads/'
    file.save(upload_path + filename)
    full_path = os.path.join(upload_path, filename)
    width = 320
    height = 256

    im = Image.open(full_path)
    i_width, i_height = im.size

    rgb_im = im.convert('RGB')

    if i_width > i_height:
        rgb_im.thumbnail((height, i_width), Image.ANTIALIAS)
    else:
        rgb_im.thumbnail((width, i_height), Image.ANTIALIAS)

    rgb_im.save(preview_path, "JPEG")
    imgfile = open(preview_path, 'rb').read()
    b64img = str(base64.b64encode(imgfile), 'utf-8')
    b64imgfile = open('images/previews/' + file_id + '.base64', 'w')

    for line in b64img:
        b64imgfile.write(line)

    os.remove(preview_path)

    return {'filename': filename, 'file_id': file_id}

@app.route('/file', methods=['DELETE'])
def delete_photo():
    file = request.form.get('file')
    file_id = request.form.get('file_id')
    os.remove('images/previews/' + file_id + '.base64')
    os.remove('images/uploads/' + file)
    return {'success': True}

@app.route('/file/original', methods=['GET'])
def original_file():
    file = request.form.get('file')
    imgfile = open('/previews/' + file, 'rb').read()
    b64img = str(base64.b64encode(imgfile), 'utf-8')
    return {content: b64img}

@app.route('/file/preview', methods=['GET'])
def preview_file():
    file_id = request.args.get('file_id')
    with open('images/previews/' + file_id + '.base64', "rb") as image_file:
        file_content = image_file.read()
    
    return file_content.decode('utf-8')

if __name__ == '__main__':
    app.run(debug=True)
