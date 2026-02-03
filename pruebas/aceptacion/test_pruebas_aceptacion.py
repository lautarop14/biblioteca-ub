import biblioteca_core as core


# =========================
# AUTENTICACIÓN
# =========================

def test_01_login_exitoso(client):
    r = client.post("/login", data={"usuario": "admin", "password": "admin123"})
    assert r.status_code == 302


def test_02_login_invalido(client):
    r = client.post("/login", data={"usuario": "zzz", "password": "yyy"})
    assert "Usuario o contraseña inválidos" in r.data.decode("utf-8")


def test_03_logout(client, login_admin):
    r = client.get("/logout", follow_redirects=True)
    assert "Sesión cerrada" in r.data.decode("utf-8")


# =========================
# CAMBIO DE CONTRASEÑA
# =========================

def test_04_cambio_password_exitoso(client, login_admin):
    r = client.post("/cambiar_password", data={
        "password_actual": "admin123",
        "nueva_password": "abcd1234",
        "confirmar_password": "abcd1234"
    })
    assert r.status_code == 302


def test_05_password_actual_incorrecta(client, login_admin):
    r = client.post("/cambiar_password", data={
        "password_actual": "incorrecta",
        "nueva_password": "abcd",
        "confirmar_password": "abcd"
    })
    assert "Contraseña actual incorrecta" in r.data.decode("utf-8")


def test_06_nueva_password_invalida(client, login_admin):
    r = client.post("/cambiar_password", data={
        "password_actual": "admin123",
        "nueva_password": "12",
        "confirmar_password": "12"
    })
    assert b"al menos 4 caracteres" in r.data


# =========================
# USUARIOS
# =========================

def test_07_agregar_usuario_lector(client, login_admin):
    r = client.post("/usuarios/nuevo", data={
        "usuario": "lector_ok",
        "nombre_completo": "Lector OK",
        "password": "1234",
        "confirmar_password": "1234"
    })
    assert b"creado exitosamente" in r.data


def test_08_agregar_usuario_lector_invalido(client, login_admin):
    r = client.post("/usuarios/nuevo", data={
        "usuario": "admin",
        "nombre_completo": "Administrador Segundo",
        "password": "as8731",
        "confirmar_password": "as8731"
    })
    assert r.status_code == 200


def test_09_agregar_usuario_lector_por_lector(client, login_lector):
    r = client.get("/usuarios/nuevo")
    assert r.status_code == 302


def test_10_eliminar_usuario_lector(client, login_admin):
    core.crear_usuario_lector("lector_borrar", "Borrar", "1234")
    usuarios = core.listar_usuarios()
    lector = next(u for u in usuarios if u["usuario"] == "lector_borrar")
    r = client.post(f"/usuarios/eliminar/{lector['id']}")
    assert r.status_code == 302


def test_11_eliminar_usuario_lector_inexistente(client, login_admin):
    r = client.post("/usuarios/eliminar/99999")
    assert r.status_code == 302


def test_12_eliminar_usuario_por_lector(client, login_lector):
    r = client.post("/usuarios/eliminar/1")
    assert r.status_code == 302


def test_13_lista_usuarios(client, login_admin):
    r = client.get("/usuarios")
    assert r.status_code == 200


def test_14_lista_usuarios_por_lector(client, login_lector):
    r = client.get("/usuarios")
    assert r.status_code == 302


# =========================
# LIBROS
# =========================

def test_15_lista_libros_con_datos(client, login_admin):
    r = client.get("/libros")
    assert r.status_code == 200


def test_16_alta_libro_completa(client, login_admin):
    r = client.post("/libros/nuevo", data={
        "titulo": "Libro Alta",
        "autores": "Autor Uno",
        "paginas": "100",
        "isbn": "111",
        "asignatura": "Programación I"
    })
    assert r.status_code == 302


def test_17_alta_libro_fallida(client, login_admin):
    r = client.post("/libros/nuevo", data={"titulo": ""})
    assert b"Error al agregar libro" in r.data


def test_18_editar_libro(client, login_admin):
    core.insertar_libro_dict("Editar", ["Autor"], 10, None, "")
    libro = core.buscar_libro_por_titulo("Editar")[0]
    r = client.post(f"/libros/editar/{libro['id']}", data={
        "titulo": "Editado",
        "autores": "Autor",
        "paginas": "20",
        "isbn": "222",
        "asignatura": ""
    })
    assert r.status_code == 302


def test_19_editar_libro_campos_invalidos(client, login_admin):
    r = client.post("/libros/editar/99999", data={})
    assert r.status_code == 302


def test_20_eliminar_libro(client, login_admin):
    core.insertar_libro_dict("Eliminar", ["Autor"], 10, None, "")
    libro = core.buscar_libro_por_titulo("Eliminar")[0]
    r = client.post(f"/libros/eliminar/{libro['id']}")
    assert r.status_code == 302


def test_21_eliminar_libro_inexistente(client, login_admin):
    r = client.post("/libros/eliminar/99999")
    assert r.status_code == 302


def test_22_alta_libro_por_lector(client, login_lector):
    r = client.get("/libros/nuevo")
    assert r.status_code == 302


def test_23_editar_libro_por_lector(client, login_lector):
    r = client.get("/libros/editar/1")
    assert r.status_code == 302


def test_24_eliminar_libro_por_lector(client, login_lector):
    r = client.post("/libros/eliminar/1")
    assert r.status_code == 302


# =========================
# PRÉSTAMOS
# =========================

def test_25_prestamo_libro_disponible(client, login_lector):
    core.insertar_libro_dict("Prestamo", ["Autor"], 10, None, "")
    libro = core.buscar_libro_por_titulo("Prestamo")[0]
    r = client.post(f"/libros/solicitar_prestamo/{libro['id']}")
    assert r.status_code == 302


def test_26_prestamo_libro_prestado(client, login_lector):
    r = client.post("/libros/solicitar_prestamo/1")
    assert r.status_code in (200, 302)


def test_27_devolver_libro_prestado(client, login_admin):
    r = client.post("/libros/registrar_devolucion/1")
    assert r.status_code == 302


def test_28_devolver_libro_disponible(client, login_admin):
    r = client.post("/libros/registrar_devolucion/1")
    assert r.status_code == 302


def test_29_devolver_libro_por_lector(client, login_lector):
    r = client.post("/libros/registrar_devolucion/1")
    assert r.status_code == 302


def test_30_lista_prestamos_activos_con_datos(client, login_admin):
    r = client.get("/prestamos")
    assert r.status_code == 200


def test_31_lista_prestamos_activos_vacia(client, login_admin):
    prestamos = core.obtener_prestamos_activos()
    assert isinstance(prestamos, list)


# =========================
# BÚSQUEDAS Y LISTADOS
# =========================

def test_32_lista_libros_vacia(client, login_admin):
    r = client.get("/libros")
    assert r.status_code == 200


def test_33_busqueda_titulo_exitosa(client, login_admin):
    r = client.post("/buscar/titulo", data={"titulo": "Libro"})
    assert r.status_code == 200


def test_34_busqueda_titulo_no_exitosa(client, login_admin):
    r = client.post("/buscar/titulo", data={"titulo": "XYZ"})
    assert b"Libro no encontrado" in r.data


def test_35_busqueda_autor_exitosa(client, login_admin):
    r = client.post("/buscar/autor", data={"autor": "Autor"})
    assert r.status_code == 200


def test_36_busqueda_autor_no_exitosa(client, login_admin):
    r = client.post("/buscar/autor", data={"autor": "Nadie"})
    assert b"No se encontraron libros" in r.data


def test_37_busqueda_asignatura_con_eleccion(client, login_admin):
    r = client.post("/buscar/asignatura", data={"asignatura": "Programación"})
    assert r.status_code == 200


def test_38_busqueda_asignatura_sin_eleccion(client, login_admin):
    r = client.post("/buscar/asignatura", data={"asignatura": ""})
    assert r.status_code == 200


def test_39_listado_exitoso(client, login_admin):
    r = client.get("/libros")
    assert r.status_code == 200


def test_40_listado_vacio(client, login_admin):
    r = client.get("/libros")
    assert r.status_code == 200

