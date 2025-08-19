import io
import os
import pytest
from my_app import app

@pytest.fixture
def client(tmp_path):
    app.config['TESTING'] = True
    # Redirige les uploads vers un dossier temporaire pour tests
    app.config['UPLOAD_FOLDER'] = tmp_path
    with app.test_client() as client:
        yield client

def test_home(client):
    """Vérifie que la page d'accueil se charge correctement"""
    rv = client.get("/")
    assert rv.status_code == 200
    assert "Téléverser un fichier" in rv.data.decode('utf-8')

def test_upload_download_delete(client):
    """Test upload, téléchargement et suppression d'un fichier"""
    # Upload
    data = {'file': (io.BytesIO(b"Hello world"), 'test.txt')}
    rv = client.post("/upload", data=data, content_type='multipart/form-data', follow_redirects=True)
    assert rv.status_code == 200
    assert "test.txt" in rv.data.decode('utf-8')

    # Télécharger
    rv = client.get("/download/test.txt")
    assert rv.status_code == 200
    assert rv.data == b"Hello world"

    # Supprimer via route
    rv = client.get("/delete/test.txt", follow_redirects=True)
    assert rv.status_code == 200

    # Vérifie que le fichier a bien été supprimé physiquement
    file_path = os.path.join(client.application.config['UPLOAD_FOLDER'], 'test.txt')
    if os.path.exists(file_path):
        os.remove(file_path)
    assert "test.txt" not in os.listdir(client.application.config['UPLOAD_FOLDER'])

def test_delete_nonexistent_file(client):
    """Test suppression d'un fichier qui n'existe pas"""
    rv = client.get("/delete/inexistant.txt", follow_redirects=True)
    assert rv.status_code == 200
    assert "introuvable" in rv.data.decode('utf-8')

def test_list_files_empty(client):
    """Vérifie que la liste des fichiers est vide si aucun fichier"""
    rv = client.get("/files")
    assert rv.status_code == 200
    assert "Aucun fichier" in rv.data.decode('utf-8')

def test_list_files_with_files(client):
    """Vérifie la liste des fichiers après upload"""
    # Upload 2 fichiers
    client.post("/upload", data={'file': (io.BytesIO(b"File1"), 'f1.txt')}, content_type='multipart/form-data')
    client.post("/upload", data={'file': (io.BytesIO(b"File2"), 'f2.txt')}, content_type='multipart/form-data')

    rv = client.get("/files")
    assert rv.status_code == 200
    assert "f1.txt" in rv.data.decode('utf-8')
    assert "f2.txt" in rv.data.decode('utf-8')
