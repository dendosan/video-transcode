import os
from flask import Flask, render_template, request, redirect, send_file
from s3_util import list_files, download_file, upload_file

app = Flask(__name__)
UPLOAD_FOLDER = "uploads"
ORIGINALS_BUCKET = "originalvideos"
MODIFIED_BUCKET = "modifiedvideos"


@app.route("/")
def entry_point():
    originals = list_files(ORIGINALS_BUCKET)
    modified = list_files(MODIFIED_BUCKET)
    return render_template('s3.html', originals=originals, modified=modified)


@app.route("/upload", methods=['POST'])
def upload():
    if request.method == "POST":
        f = request.files['file']
        f.save(f"uploads/{f.filename}")
        upload_file(f"uploads/{f.filename}", ORIGINALS_BUCKET)

        return redirect("/")


@app.route("/download/uploads/<filename>", methods=['GET'])
def download(filename):
    if request.method == 'GET':
        output = download_file(filename, ORIGINALS_BUCKET)

        return send_file(output, as_attachment=True)


# @app.route("/modified/uploads/<filename>", methods=['GET'])
# def modified(filename):
#     if request.method == 'GET':
#         output = download_file(filename, MODIFIED_BUCKET)

#         return send_file(output, as_attachment=True)


if __name__ == '__main__':
    app.run(debug=True)
