import os
import time
import logging
from logging.handlers import RotatingFileHandler
from flask import Flask, render_template, request, redirect, url_for, send_from_directory, flash

def create_app():
    app = Flask(__name__)
    app.secret_key = "secret"

    # --------------------------
    # Dossier uploads
    # --------------------------
    UPLOAD_FOLDER = os.path.join(os.path.dirname(__file__), "uploads")
    app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
    os.makedirs(UPLOAD_FOLDER, exist_ok=True)

    # --------------------------
    # Logging
    # --------------------------
    if not app.logger.handlers:  # éviter reconfiguration
        if not os.path.exists("logs"):
            os.makedirs("logs")
        handler = RotatingFileHandler("logs/app.log", maxBytes=1000000, backupCount=5)
        formatter = logging.Formatter("[%(asctime)s] %(levelname)s in %(module)s: %(message)s")
        handler.setFormatter(formatter)
        app.logger.addHandler(handler)
        app.logger.setLevel(logging.INFO)

    # --------------------------
    # Routes
    # --------------------------
    @app.route("/", methods=["GET"])
    def index():
        """Page d'accueil : seulement accueil / lien vers upload"""
        app.logger.info("Page d'accueil visitée")
        return render_template("index.html")  # Texte attendu : "Bienvenue sur l'application Flask"

    @app.route("/upload", methods=["GET", "POST"])
    def upload_file():
        """Afficher formulaire et gérer upload"""
        if request.method == "POST":
            if "file" not in request.files:
                flash("Aucun fichier sélectionné", "error")
                app.logger.warning("Upload échoué : aucun fichier dans request")
                return redirect(url_for("upload_file"))

            file = request.files["file"]
            if file.filename == "":
                flash("Nom de fichier vide", "error")
                app.logger.warning("Upload échoué : nom de fichier vide")
                return redirect(url_for("upload_file"))

            file_path = os.path.join(app.config['UPLOAD_FOLDER'], file.filename)
            file.save(file_path)
            flash(f"{file.filename} téléversé", "success")
            app.logger.info(f"Fichier uploadé : {file.filename}")
            return redirect(url_for("list_files"))

        return render_template("upload.html")  # Texte attendu : "Uploader un fichier"

    @app.route("/files", methods=["GET"])
    def list_files():
        """Afficher la liste des fichiers"""
        files = os.listdir(app.config['UPLOAD_FOLDER'])
        app.logger.info("Liste des fichiers consultée")
        return render_template("list.html", files=files)

    @app.route("/download/<filename>")
    def download_file(filename):
        """Télécharger un fichier existant"""
        file_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        if os.path.exists(file_path):
            app.logger.info(f"Téléchargement fichier : {filename}")
            return send_from_directory(app.config['UPLOAD_FOLDER'], filename, as_attachment=True)
        else:
            flash(f"Fichier {filename} introuvable", "error")
            app.logger.warning(f"Téléchargement échoué, fichier introuvable : {filename}")
            return redirect(url_for("list_files"))

    @app.route("/delete/<filename>")
    def delete_file(filename):
        """Supprimer un fichier"""
        file_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        if os.path.exists(file_path):
            try:
                time.sleep(0.1)
                os.remove(file_path)
                flash(f"{filename} supprimé", "success")
                app.logger.info(f"Fichier supprimé : {filename}")
            except PermissionError:
                flash(f"Impossible de supprimer {filename}. Le fichier est utilisé.", "error")
                app.logger.error(f"Erreur suppression fichier utilisé : {filename}")
        else:
            flash(f"Fichier {filename} introuvable", "error")
            app.logger.warning(f"Tentative suppression fichier introuvable : {filename}")
        return redirect(url_for("list_files"))

    return app

# --------------------------
# Exécution directe
# --------------------------
if __name__ == "__main__":
    app = create_app()
    app.run(host="0.0.0.0", port=5000, debug=True)
