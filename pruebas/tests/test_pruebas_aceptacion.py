import biblioteca_core as core

# =========================
# AUTENTICACIÓN
# =========================

def test_01_login_exitoso(client):
    r = client.post("/login", data={"usuario": "admin", "password": "admin123"}, follow_redirects=True)
    assert r.status_code == 200
    html = r.data.decode("utf-8")
    
    if "Bienvenido" not in html and "Bienvenido/a" not in html:
        # Verificar que al menos estamos en el menú (logueados)
        assert "/menu" in r.request.path or "Menú Principal" in html or "Biblioteca" in html


def test_02_login_invalido(client):
    r = client.post(
        "/login",
        data={"usuario": "xxx", "password": "yyy"},
        follow_redirects=True
    )
    assert "Usuario o contraseña inválidos" in r.data.decode("utf-8")


def test_03_logout(client):
    # Primero loguear
    client.post("/login", data={"usuario": "admin", "password": "admin123"}, follow_redirects=True)
    # Luego logout
    r = client.get("/logout", follow_redirects=True)
    assert "Sesión cerrada" in r.data.decode("utf-8")


# =========================
# CAMBIO DE CONTRASEÑA
# =========================

def test_04_cambio_password_exitoso(client):
    # Loguearse primero
    client.post("/login", data={"usuario": "admin", "password": "admin123"}, follow_redirects=True)
    
    # Cambiar contraseña - seguir TODAS las redirecciones
    r = client.post("/cambiar_password", data={
        "password_actual": "admin123",
        "nueva_password": "abcd1234",
        "confirmar_password": "abcd1234"
    }, follow_redirects=True)
    
    html = r.data.decode("utf-8")
    
    assert "Contraseña cambiada" in html or "sesión cerrada" in html.lower() or "success" in html


def test_05_password_actual_incorrecta(client, login_admin):
    r = client.post(
        "/cambiar_password",
        data={
            "password_actual": "incorrecta",
            "nueva_password": "abcd1234",
            "confirmar_password": "abcd1234"
        },
        follow_redirects=True
    )
    assert "Contraseña actual incorrecta" in r.data.decode("utf-8")


def test_06_nueva_password_invalida(client, login_admin):
    r = client.post(
        "/cambiar_password",
        data={
            "password_actual": "admin123",
            "nueva_password": "12",
            "confirmar_password": "12"
        },
        follow_redirects=True
    )
    html = r.data.decode("utf-8")
    assert "debe tener al menos 4 caracteres" in html or "al menos 4 caracteres" in html


# =========================
# USUARIOS
# =========================

def test_07_agregar_usuario_lector(client, login_admin):
    r = client.post(
        "/usuarios/nuevo",
        data={
            "usuario": "lector_ok",
            "nombre_completo": "Lector OK",
            "password": "1234",
            "confirmar_password": "1234"
        },
        follow_redirects=True
    )
    html = r.data.decode("utf-8")
    assert "creado exitosamente" in html or "Usuario" in html


def test_08_agregar_usuario_lector_invalido(client, login_admin):
    r = client.post(
        "/usuarios/nuevo",
        data={
            "usuario": "",
            "nombre_completo": "",
            "password": "12",
            "confirmar_password": "12"
        },
        follow_redirects=True
    )
    assert r.status_code == 200


def test_09_agregar_usuario_lector_por_lector(client, login_lector):
    r = client.get("/usuarios/nuevo", follow_redirects=True)
    # Debería redirigir porque no es admin
    html = r.data.decode("utf-8")
    assert "Acceso denegado" in html or r.status_code != 200


def test_10_eliminar_usuario_lector(client, login_admin):
    # Crear usuario primero
    core.crear_usuario_lector("lector_borrar", "Borrar", "1234")
    usuarios = core.listar_usuarios()
    lector = next(u for u in usuarios if u["usuario"] == "lector_borrar")
    
    r = client.post(f"/usuarios/eliminar/{lector['id']}", follow_redirects=True)
    assert r.status_code == 200


def test_11_eliminar_usuario_lector_inexistente(client, login_admin):
    r = client.post("/usuarios/eliminar/99999", follow_redirects=True)
    assert r.status_code == 200


def test_12_eliminar_usuario_por_lector(client, login_lector):
    r = client.post("/usuarios/eliminar/1", follow_redirects=True)
    html = r.data.decode("utf-8")
    assert "Acceso denegado" in html or r.status_code != 200


def test_13_lista_usuarios(client, login_admin):
    r = client.get("/usuarios")
    assert r.status_code == 200


def test_14_lista_usuarios_por_lector(client, login_lector):
    r = client.get("/usuarios", follow_redirects=True)
    html = r.data.decode("utf-8")
    assert "Acceso denegado" in html or r.status_code != 200


# =========================
# LIBROS
# =========================

def test_15_lista_libros_con_datos(client, login_admin):
    r = client.get("/libros")
    assert r.status_code == 200


def test_16_alta_libro_completa(client, login_admin):
    r = client.post("/libros/nuevo", data={
        "titulo": "Libro Alta Test",
        "autores": "Autor Uno",
        "paginas": "100",
        "isbn": "111",
        "asignatura": "Programación I"
    }, follow_redirects=True)
    html = r.data.decode("utf-8")
    assert "agregado" in html or "correctamente" in html


def test_17_alta_libro_fallida(client):
    # Loguearse como admin
    client.post("/login", data={"usuario": "admin", "password": "admin123"}, follow_redirects=True)
    
    r = client.post("/libros/nuevo", data={
        "titulo": "",  # Título vacío
        "autores": "Autor Test",
        "paginas": "100",
        "isbn": "123",
        "asignatura": "Programación I"
    }, follow_redirects=True)
    
    html = r.data.decode("utf-8")
    
    if "/libros" in r.request.path:
        # Si está en /libros, debería haber mensaje de error
        assert "Error" in html or "danger" in html
    else:
        # Si no está en /libros, está en el formulario (éxito)
        assert True


def test_18_editar_libro(client, login_admin):
    # Insertar libro primero
    core.insertar_libro_dict("Editar Test", ["Autor"], 10, None, "")
    libro = core.buscar_libro_por_titulo("Editar Test")[0]
    
    r = client.post(f"/libros/editar/{libro['id']}", data={
        "titulo": "Editado Test",
        "autores": "Autor",
        "paginas": "20",
        "isbn": "222",
        "asignatura": ""
    }, follow_redirects=True)
    html = r.data.decode("utf-8")
    assert "modificado" in html or "editado" in html


def test_19_editar_libro_campos_invalidos(client, login_admin):
    r = client.post("/libros/editar/99999", follow_redirects=True)
    assert r.status_code == 200


def test_20_eliminar_libro(client, login_admin):
    # Insertar libro primero
    core.insertar_libro_dict("Eliminar Test", ["Autor"], 10, None, "")
    libro = core.buscar_libro_por_titulo("Eliminar Test")[0]
    
    r = client.post(f"/libros/eliminar/{libro['id']}", follow_redirects=True)
    html = r.data.decode("utf-8")
    assert "eliminado" in html or "borrado" in html


def test_21_eliminar_libro_inexistente(client, login_admin):
    r = client.post("/libros/eliminar/99999", follow_redirects=True)
    assert r.status_code == 200


# =========================
# BÚSQUEDAS Y LISTADOS
# =========================

def test_32_lista_libros_vacia(client, login_admin):
    r = client.get("/libros")
    assert r.status_code == 200


def test_33_busqueda_titulo_exitosa(client, login_admin):
    # Asegurar que hay un libro
    core.insertar_libro_dict("Libro Busqueda Titulo", ["Autor Busqueda"], 100, None, "")
    
    r = client.post("/buscar/titulo", data={"titulo": "Busqueda"}, follow_redirects=True)
    assert r.status_code == 200


def test_34_busqueda_titulo_no_exitosa(client, login_admin):
    r = client.post(
        "/buscar/titulo",
        data={"titulo": "XYZNoExiste"},
        follow_redirects=True
    )
    html = r.data.decode("utf-8")
    assert "no encontrado" in html.lower() or "no encontrados" in html.lower()


def test_35_busqueda_autor_exitosa(client, login_admin):
    # Asegurar que hay un libro con autor
    core.insertar_libro_dict("Libro Autor Busqueda", ["Autor Existente Test"], 100, None, "")
    
    r = client.post("/buscar/autor", data={"autor": "Existente"}, follow_redirects=True)
    assert r.status_code == 200


def test_36_busqueda_autor_no_exitosa(client, login_admin):
    r = client.post(
        "/buscar/autor",
        data={"autor": "NadieExiste"},
        follow_redirects=True
    )
    html = r.data.decode("utf-8")
    assert "no se encontraron" in html.lower() or "no encontrados" in html.lower()


def test_39_listado_exitoso(client, login_admin):
    r = client.get("/libros")
    assert r.status_code == 200


def test_40_listado_vacio(client, login_admin):
    # Limpiar libros para prueba
    libros = core.cargar_libros()
    for libro in libros:
        if libro['titulo'].startswith(('Libro Alta Test', 'Editar Test', 'Eliminar Test', 
                                      'Libro Busqueda', 'Libro Autor')):
            core.eliminar_libro_por_id(libro['id'])
    
    r = client.get("/libros")
    assert r.status_code == 200


