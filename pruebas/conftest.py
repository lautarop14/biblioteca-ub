import pytest
import sys
import os

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from app import app
import biblioteca_core as core

@pytest.fixture
def client():
    app.config["TESTING"] = True
    with app.test_client() as client:
        yield client


@pytest.fixture
def login_admin(client):
    return client.post(
        "/login",
        data={"usuario": "admin", "password": "admin123"},
        follow_redirects=True
    )


@pytest.fixture
def login_lector(client):
    core.crear_usuario_lector("lector_test", "Usuario Lector", "1234")
    return client.post(
        "/login",
        data={"usuario": "lector_test", "password": "1234"},
        follow_redirects=True
    )