# conftest.py (en la raíz del proyecto)
import sys
import os
import pytest

# Añadir el directorio actual al path para que Python pueda encontrar los módulos
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

try:
    import biblioteca_core as core
    from app import app
except ImportError as e:
    print(f"Error al importar módulos: {e}")
    print(f"Directorio actual: {os.getcwd()}")
    print(f"Contenido del directorio: {os.listdir('.')}")
    raise

@pytest.fixture
def client():
    app.config['TESTING'] = True
    app.config['SECRET_KEY'] = 'test-secret-key'
    app.config['WTF_CSRF_ENABLED'] = False  # Deshabilitar CSRF para pruebas
    with app.test_client() as client:
        yield client

@pytest.fixture
def login_admin(client):
    """Fixture para loguear como admin y mantener la sesión"""
    # Primero hacer login real para asegurar que el usuario existe
    client.post('/login', data={
        'usuario': 'admin',
        'password': 'admin123'
    }, follow_redirects=True)
    
    return client

@pytest.fixture
def login_lector(client):
    """Fixture para loguear como lector"""
    # Crear usuario lector si no existe
    core.crear_usuario_lector("test_lector", "Test Lector", "1234")
    
    # Hacer login
    client.post('/login', data={
        'usuario': 'test_lector',
        'password': '1234'
    }, follow_redirects=True)
    
    return client

@pytest.fixture(autouse=True)
def setup_database():
    """Fixture para configurar la base de datos antes de cada prueba"""
    # Asegurar que las tablas existan
    core.crear_tablas()
    yield
    # Opcional: limpiar datos de prueba si es necesario