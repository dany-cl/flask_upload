from flask import Flask, request, redirect, url_for, render_template, send_from_directory
import os

app = Flask(__name__)
UPLOAD_FOLDER = "uploads"
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

# Créer le dossier uploads s'il n'existe pas
if not os.path.exists(app.config['UPLOAD_FOLDER']):
    os.makedirs(app.config['UPLOAD_FOLDER'])

@app.route("/")
def home():
    return render_template("home.html")

@app.route("/health")
def health():
    return {"status": "ok"}

@app.route("/upload", methods=["GET", "POST"])
def upload_file():
    if request.method == "POST":
        if "file" not in request.files:
            return "Aucun fichier sélectionné"
        file = request.files["file"]
        if file.filename == "":
            return "Nom de fichier vide"
        file.save(os.path.join(app.config['UPLOAD_FOLDER'], file.filename))
        return redirect(url_for("list_files"))
    return render_template("upload.html")

@app.route("/files")
def list_files():
    files = os.listdir(app.config['UPLOAD_FOLDER'])
    return render_template("list.html", files=files)

@app.route("/download/<filename>")
def download_file(filename):
    return send_from_directory(app.config['UPLOAD_FOLDER'], filename, as_attachment=True)

@app.route("/delete/<filename>")
def delete_file(filename):
    file_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
    if os.path.exists(file_path):
        os.remove(file_path)
        return redirect(url_for("list_files"))
    return f"Fichier {filename} introuvable", 404

if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0", port=5000)
