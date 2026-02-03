# conftest.py
import pytest
import biblioteca_core as core
from app import app

@pytest.fixture
def client():
    app.config['TESTING'] = True
    app.config['SECRET_KEY'] = 'test-secret-key'
    with app.test_client() as client:
        yield client

@pytest.fixture
def login_admin(client):
    """Fixture para loguear como admin y mantener la sesión"""
    with client.session_transaction() as session:
        # Simular login manualmente en la sesión
        session['logged_in'] = True
        session['usuario'] = 'admin'
        session['usuario_id'] = 1
        session['nombre'] = 'Administrador Principal'
        session['rol'] = 'admin'
    return client

@pytest.fixture
def login_lector(client):
    """Fixture para loguear como lector"""
    # Crear usuario lector primero si no existe
    core.crear_usuario_lector("test_lector", "Test Lector", "1234")
    
    with client.session_transaction() as session:
        # Obtener ID del usuario
        usuarios = core.listar_usuarios()
        test_user = next(u for u in usuarios if u['usuario'] == 'test_lector')
        
        session['logged_in'] = True
        session['usuario'] = 'test_lector'
        session['usuario_id'] = test_user['id']
        session['nombre'] = 'Test Lector'
        session['rol'] = 'lector'
    return client

@pytest.fixture(autouse=True)
def setup_database():
    """Fixture para configurar la base de datos antes de cada prueba"""
    # Asegurar que las tablas existan
    core.crear_tablas()
    yield
    # Limpiar después de cada prueba si es necesario