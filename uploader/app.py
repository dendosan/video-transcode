import os
from flask import Flask, render_template, request, redirect, send_file
from s3_util import list_files, download_file, upload_file

app = Flask(__name__)
UPLOAD_FOLDER = "uploads"
BUCKET = "originalvideos"


@app.route("/")
def entry_point():
    contents = list_files(BUCKET)
    return render_template('s3.html', contents=contents)


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


if __name__ == '__main__':
    app.run(debug=True)
