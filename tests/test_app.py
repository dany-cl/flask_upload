import sys
import os
import pytest

# Ajouter le dossier racine au PYTHONPATH
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from app import app

@pytest.fixture
def client():
    app.config['TESTING'] = True
    with app.test_client() as client:
        yield client

def test_home(client):
    rv = client.get("/")
    assert rv.status_code == 200
    assert b"Bienvenue sur l'application Flask Upload" in rv.data

def test_health(client):
    rv = client.get("/health")
    assert rv.status_code == 200
    assert rv.json == {"status": "ok"}
