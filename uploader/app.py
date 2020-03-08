import os
from flask import Flask, render_template, request, redirect, send_file
from s3_util import list_files, download_file, upload_file

app = Flask(__name__)
UPLOAD_FOLDER = "uploads"
BUCKET = "originalvideos"
CONVERTED_BUCKET = "modifiedvideos"


@app.route("/")
def entry_point():
    originals = list_files(BUCKET)
    converted = list_files(CONVERTED_BUCKET)
    return render_template('s3.html', originals=originals, converted=converted)


@app.route("/upload", methods=['POST'])
def upload():
    if request.method == "POST":
        f = request.files['file']
        f.save(f"uploads/{f.filename}")
        upload_file(f"uploads/{f.filename}", BUCKET)

        return redirect("/")


@app.route("/download/uploads/<filename>", methods=['GET'])
def download(filename):
    if request.method == 'GET':
        output = download_file(filename, BUCKET)

        return send_file(output, as_attachment=True)


@app.route("/converted/uploads/<filename>", methods=['GET'])
def converted(filename):
    if request.method == 'GET':
        output = download_file(filename, CONVERTED_BUCKET)

        return send_file(output, as_attachment=True)


if __name__ == '__main__':
    app.run(debug=True)
