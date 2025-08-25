import io
import os
import pytest
import sys

# Assure que l'on peut importer my_app
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from my_app import create_app

@pytest.fixture
def client(tmp_path):
    app = create_app()
    app.config['TESTING'] = True
    # Redirige les uploads vers un dossier temporaire pour tests
    app.config['UPLOAD_FOLDER'] = tmp_path
    with app.test_client() as client:
        yield client

def test_home_page(client):
    """Vérifie que la page d'accueil se charge correctement"""
    rv = client.get("/")
    assert rv.status_code == 200
    assert "Bienvenue sur l'application Flask" in rv.data.decode('utf-8')

def test_upload_page_get(client):
    """Vérifie que la page upload (GET) se charge correctement"""
    rv = client.get("/upload")
    assert rv.status_code == 200
    assert "Uploader un fichier" in rv.data.decode('utf-8')

def test_upload_file_post(client):
    """Test upload d'un fichier via POST"""
    data = {'file': (io.BytesIO(b"Hello world"), 'test.txt')}
    rv = client.post("/upload", data=data, content_type='multipart/form-data', follow_redirects=True)
    assert rv.status_code == 200
    # Vérifie que le fichier apparaît dans la liste
    assert "test.txt" in rv.data.decode('utf-8')
    # Vérifie qu'il a été physiquement créé
    file_path = os.path.join(client.application.config['UPLOAD_FOLDER'], 'test.txt')
    assert os.path.exists(file_path)

def test_download_file(client):
    """Test téléchargement d'un fichier"""
    # Upload d'abord
    client.post("/upload", data={'file': (io.BytesIO(b"Hello world"), 'f1.txt')}, content_type='multipart/form-data')
    rv = client.get("/download/f1.txt")
    assert rv.status_code == 200
    assert rv.data == b"Hello world"

def test_delete_file(client):
    """Test suppression d'un fichier"""
    # Upload d'abord
    client.post("/upload", data={'file': (io.BytesIO(b"Hello"), 'fdel.txt')}, content_type='multipart/form-data')
    rv = client.get("/delete/fdel.txt", follow_redirects=True)
    assert rv.status_code == 200
    assert "fdel.txt" not in os.listdir(client.application.config['UPLOAD_FOLDER'])

def test_delete_nonexistent_file(client):
    """Test suppression d'un fichier inexistant"""
    rv = client.get("/delete/inexistant.txt", follow_redirects=True)
    assert rv.status_code == 200
    assert "introuvable" in rv.data.decode('utf-8')

def test_list_files_empty(client):
    """Vérifie que la liste est vide si aucun fichier"""
    rv = client.get("/files")
    assert rv.status_code == 200
    assert "Aucun fichier uploadé" in rv.data.decode('utf-8')

def test_list_files_with_files(client):
    """Vérifie que la liste montre tous les fichiers après upload"""
    client.post("/upload", data={'file': (io.BytesIO(b"File1"), 'f1.txt')}, content_type='multipart/form-data')
    client.post("/upload", data={'file': (io.BytesIO(b"File2"), 'f2.txt')}, content_type='multipart/form-data')
    rv = client.get("/files")
    content = rv.data.decode('utf-8')
    assert "f1.txt" in content
    assert "f2.txt" in content
 