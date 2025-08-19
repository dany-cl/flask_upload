from flask import Flask, request, redirect, url_for, render_template, send_from_directory, flash
import os

app = Flask(__name__)
app.secret_key = "secret"
app.config['UPLOAD_FOLDER'] = os.path.join(os.path.dirname(__file__), 'uploads')
os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)

@app.route("/")
def index():
    files = os.listdir(app.config['UPLOAD_FOLDER'])
    return render_template("index.html", files=files)

@app.route("/upload", methods=["POST"])
def upload_file():
    if 'file' not in request.files:
        flash("Aucun fichier sélectionné")
        return redirect(url_for('index'))
    file = request.files['file']
    if file.filename == '':
        flash("Aucun fichier sélectionné")
        return redirect(url_for('index'))
    file_path = os.path.join(app.config['UPLOAD_FOLDER'], file.filename)
    file.save(file_path)
    flash(f"{file.filename} téléversé avec succès")
    return redirect(url_for('index'))

@app.route("/download/<filename>")
def download_file(filename):
    file_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
    if os.path.exists(file_path):
        # Lire le fichier dans un flux pour éviter le verrouillage
        with open(file_path, "rb") as f:
            data = f.read()
        from flask import Response
        return Response(data, headers={
            "Content-Disposition": f"attachment; filename={filename}"
        })
    else:
        flash(f"{filename} n'existe pas")
        return redirect(url_for('index'))

@app.route("/delete/<filename>")
def delete_file(filename):
    file_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
    if os.path.exists(file_path):
        try:
            os.remove(file_path)
            flash(f"{filename} supprimé avec succès")
        except PermissionError:
            import time
            for _ in range(5):
                try:
                    os.remove(file_path)
                    flash(f"{filename} supprimé avec succès après attente")
                    break
                except PermissionError:
                    time.sleep(0.1)
            else:
                flash(f"Impossible de supprimer {filename}")
    else:
        flash(f"{filename} n'existe pas")
    return redirect(url_for('index'))

if __name__ == "__main__":
    app.run(debug=True)
