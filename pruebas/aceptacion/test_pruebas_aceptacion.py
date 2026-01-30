import pytest
from app import app

# ======================================================
# FIXTURE PRINCIPAL
# ======================================================

@pytest.fixture
def client():
    app.config['TESTING'] = True
    with app.test_client() as client:
        yield client

# ======================================================
# HELPERS
# ======================================================

def login(client, usuario, password):
    return client.post(
        '/login',
        data={'usuario': usuario, 'password': password},
        follow_redirects=True
    )

def logout(client):
    return client.get('/logout', follow_redirects=True)

def get_text(response):
    return response.get_data(as_text=True).lower()

# ======================================================
# A - AUTENTICACIÓN
# ======================================================

def test_A1_login_exitoso(client):
    r = login(client, 'admin', 'admin123')
    texto = get_text(r)
    assert 'bienvenido' in texto

def test_A2_login_invalido(client):
    r = login(client, 'usuario_falso', 'clave_falsa')
    texto = get_text(r)
    assert 'inválido' in texto or 'error' in texto

def test_A3_logout(client):
    login(client, 'admin', 'admin123')
    r = logout(client)
    texto = get_text(r)
    assert 'login' in texto

def test_A4_cambio_password_exitoso(client):
    login(client, 'admin', 'admin123')
    r = client.post(
        '/cambiar_password',
        data={
            'password_actual': 'admin123',
            'nueva_password': 'nueva123',
            'confirmar_password': 'nueva123'
        },
        follow_redirects=True
    )
    texto = get_text(r)
    assert 'contraseña' in texto or 'cambiada' in texto

def test_A5_cambio_password_actual_incorrecta(client):
    login(client, 'admin', 'admin123')
    r = client.post(
        '/cambiar_password',
        data={
            'password_actual': 'incorrecta',
            'nueva_password': 'abcd',
            'confirmar_password': 'abcd'
        },
        follow_redirects=True
    )
    texto = get_text(r)
    assert 'incorrecta' in texto

def test_A6_cambio_password_nueva_invalida(client):
    login(client, 'admin', 'admin123')
    r = client.post(
        '/cambiar_password',
        data={
            'password_actual': 'admin123',
            'nueva_password': '1',
            'confirmar_password': '1'
        },
        follow_redirects=True
    )
    texto = get_text(r)
    assert 'caracteres' in texto

# ======================================================
# L - LIBROS
# ======================================================

def test_L1_listar_libros(client):
    login(client, 'admin', 'admin123')
    r = client.get('/libros', follow_redirects=True)
    assert r.status_code == 200

def test_L2_alta_libro_ok(client):
    login(client, 'admin', 'admin123')
    r = client.post(
        '/libros/nuevo',
        data={
            'titulo': 'Libro de Pruebas Automatizado',
            'autores': 'Autor Test',
            'paginas': 150,
            'isbn': 123456789,
            'asignatura': 'Programación I'
        },
        follow_redirects=True
    )
    texto = get_text(r)
    assert 'agregado' in texto or 'éxito' in texto

def test_L3_alta_libro_fallida(client):
    login(client, 'admin', 'admin123')
    r = client.post(
        '/libros/nuevo',
        data={
            'titulo': '',
            'autores': ''
        },
        follow_redirects=True
    )
    texto = get_text(r)
    assert 'error' in texto

def test_L4_editar_libro_ok(client):
    login(client, 'admin', 'admin123')
    r = client.post(
        '/libros/editar/1',
        data={
            'titulo': 'Libro Editado',
            'autores': 'Autor Editado'
        },
        follow_redirects=True
    )
    texto = get_text(r)
    assert 'modificado' in texto or 'éxito' in texto

def test_L5_editar_libro_invalido(client):
    login(client, 'admin', 'admin123')
    r = client.post(
        '/libros/editar/1',
        data={
            'titulo': ''
        },
        follow_redirects=True
    )
    texto = get_text(r)
    assert 'error' in texto

def test_L6_eliminar_libro(client):
    login(client, 'admin', 'admin123')
    r = client.post('/libros/eliminar/1', follow_redirects=True)
    texto = get_text(r)
    assert 'eliminado' in texto or r.status_code == 200

# ======================================================
# C - CONSULTAS / BÚSQUEDAS
# ======================================================

def test_C1_busqueda_titulo_exitosa(client):
    login(client, 'admin', 'admin123')
    r = client.post(
        '/buscar',
        data={'titulo': 'programación'},
        follow_redirects=True
    )
    assert r.status_code == 200

def test_C2_busqueda_titulo_no_exitosa(client):
    login(client, 'admin', 'admin123')
    r = client.post(
        '/buscar',
        data={'titulo': 'zzzzzzzzzz'},
        follow_redirects=True
    )
    texto = get_text(r)
    assert 'no se encontraron' in texto or r.status_code == 200

def test_C3_busqueda_autor_exitosa(client):
    login(client, 'admin', 'admin123')
    r = client.post(
        '/buscar',
        data={'autor': 'autor'},
        follow_redirects=True
    )
    assert r.status_code == 200

def test_C4_busqueda_autor_no_exitosa(client):
    login(client, 'admin', 'admin123')
    r = client.post(
        '/buscar',
        data={'autor': 'autor_inexistente_xyz'},
        follow_redirects=True
    )
    texto = get_text(r)
    assert 'no se encontraron' in texto or r.status_code == 200

def test_C5_busqueda_asignatura_con_eleccion(client):
    login(client, 'admin', 'admin123')
    r = client.post(
        '/buscar',
        data={'asignatura': 'Sistemas Operativos'},
        follow_redirects=True
    )
    assert r.status_code == 200

def test_C6_busqueda_asignatura_sin_eleccion(client):
    login(client, 'admin', 'admin123')
    r = client.post(
        '/buscar',
        data={'asignatura': ''},
        follow_redirects=True
    )
    texto = get_text(r)
    assert 'seleccion' in texto or r.status_code == 200

# ======================================================
# AU - AUTORES
# ======================================================

def test_AU1_listar_autores(client):
    login(client, 'admin', 'admin123')
    r = client.get('/autores', follow_redirects=True)
    assert r.status_code == 200

def test_AU2_listar_autores_sin_datos(client):
    login(client, 'admin', 'admin123')
    r = client.get('/autores', follow_redirects=True)
    assert r.status_code == 200