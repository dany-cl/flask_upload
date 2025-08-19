import os
import time
from flask import Flask, render_template, request, redirect, url_for, send_from_directory, flash

app = Flask(__name__)
app.secret_key = "secret"
UPLOAD_FOLDER = os.path.join(os.path.dirname(__file__), "uploads")
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

os.makedirs(UPLOAD_FOLDER, exist_ok=True)

@app.route("/")
def index():
    files = os.listdir(app.config['UPLOAD_FOLDER'])
    return render_template("index.html", files=files)

@app.route("/upload", methods=["POST"])
def upload_file():
    if "file" not in request.files:
        flash("Aucun fichier sélectionné", "error")
        return redirect(url_for("index"))

    file = request.files["file"]
    if file.filename == "":
        flash("Nom de fichier vide", "error")
        return redirect(url_for("index"))

    file_path = os.path.join(app.config['UPLOAD_FOLDER'], file.filename)
    file.save(file_path)
    flash(f"{file.filename} téléversé", "success")
    return redirect(url_for("index"))

@app.route("/download/<filename>")
def download_file(filename):
    file_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
    if os.path.exists(file_path):
        return send_from_directory(app.config['UPLOAD_FOLDER'], filename, as_attachment=True)
    else:
        flash(f"Fichier {filename} introuvable", "error")
        return redirect(url_for("index"))

@app.route("/delete/<filename>")
def delete_file(filename):
    file_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
    if os.path.exists(file_path):
        try:
            # Petite pause pour libérer le fichier sous Windows
            time.sleep(0.1)
            os.remove(file_path)
            flash(f"{filename} supprimé", "success")
        except PermissionError:
            flash(f"Impossible de supprimer {filename}. Le fichier est utilisé.", "error")
    else:
        flash(f"Fichier {filename} introuvable", "error")
    return redirect(url_for("index"))

@app.route("/files")
def list_files():
    files = os.listdir(app.config['UPLOAD_FOLDER'])
    if not files:
        flash("Aucun fichier", "info")
    return render_template("index.html", files=files)

if __name__ == "__main__":
    app.run(debug=True)
