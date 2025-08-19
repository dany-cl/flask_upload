import os
import io
import pytest
from my_app import app
import time
import shutil

@pytest.fixture
def client():
    app.config['TESTING'] = True
    temp_folder = os.path.join(os.path.dirname(__file__), 'temp_uploads')
    os.makedirs(temp_folder, exist_ok=True)
    app.config['UPLOAD_FOLDER'] = temp_folder

    with app.test_client() as client:
        yield client

    # Cleanup après les tests
    for f in os.listdir(temp_folder):
        file_path = os.path.join(temp_folder, f)
        for _ in range(5):  # essayer 5 fois de supprimer si verrouillé
            try:
                os.remove(file_path)
                break
            except PermissionError:
                time.sleep(0.1)
        else:
            print(f"Impossible de supprimer {file_path} après plusieurs essais")
    shutil.rmtree(temp_folder, ignore_errors=True)

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

    # Supprimer
    rv = client.get("/delete/test.txt", follow_redirects=True)
    assert rv.status_code == 200
    assert "test.txt" not in os.listdir(client.application.config['UPLOAD_FOLDER'])

def test_delete_nonexistent_file(client):
    """Test suppression d'un fichier inexistant"""
    rv = client.get("/delete/nonexistent.txt", follow_redirects=True)
    assert rv.status_code == 200
    assert b"nonexistent.txt" in rv.data  # devrait afficher un message flash
