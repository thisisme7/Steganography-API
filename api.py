#!/usr/bin/env python3
from flask import Flask, request, redirect, url_for, render_template, send_from_directory, session
from werkzeug.utils import secure_filename
import steganography_app as Steg


app = Flask(__name__)
app.secret_key = 'n7v836bw58429m35nv7e6349n832' # secret key for session management

ALLOWED_EXTENSIONS = {'txt', 'png'}

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


@app.route("/", methods=['GET', 'POST'])
def main():
    if request.method == 'POST':
        # Check if both files are present
        if 'image' not in request.files or 'text' not in request.files:
            return 'Missing files', 400
        
        image_file = request.files['image']
        text_file = request.files['text']
        
        # Check file extensions
        if image_file.filename.endswith('.png') and text_file.filename.endswith('.txt'):
            
            # Save the files to a desired location
            image_file_name = secure_filename(image_file.filename)
            image_file.save('images/' + image_file_name)
            
            text_file_name = secure_filename(text_file.filename)
            text_file.save('messages/' + text_file_name)
            
            key, stg_pic = Steg.Embedder(picture=image_file_name, textfile=text_file_name)
            
            # Store the key and filename in the session
            session['key'] = key
            
            return redirect(url_for('download', file=stg_pic, key=key))

        else:
            return "Invalid file format, items must be txt and png", 400
            
    return render_template("index.html")

@app.route("/download/<path:file>/<key>", methods=['GET', 'POST'])
def download(file, key):
    path = "/var/www/Steganography/modified"
    if request.method == 'POST' and 'key' in session:
        return send_from_directory(path, file, as_attachment=True)
    if 'key' in session:
        return render_template("download.html", key=key, file=file)

@app.route("/decode", methods=['GET', 'POST'])
def decode():
    if 'image' not in request.files or 'password' not in request.form:
        return 'Missing files', 400
        
    stegged = request.files['image']
    key = request.form['password']
    
    if stegged.filename.endswith('.png') and key:
        stegged_name = secure_filename(stegged.filename)
        stegged.save('storage/' + stegged_name)
        plainmessage = Steg.Extractor(picture=stegged_name, key=key)
        return render_template('index.html', plainmessage=plainmessage)
        
    else:
        return "Invalid file format", 400
if __name__ == '__main__':
    app.run(host="techriot.net", port=5000)
