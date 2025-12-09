# tests_biblioteca_completo.py
# Contiene tests unitarios (fake DB) + tests de rutas Flask (login/logout/change password)
import hashlib
import biblioteca_core as core
import pytest
import json

# Intentamos importar la app Flask; si falla, algunos tests de rutas se saltarán.
try:
    from app import app as flask_app
    HAS_FLASK_APP = True
except Exception:
    HAS_FLASK_APP = False

#
# --- Fake in-memory DB (simula lo suficiente para las funciones testadas) ---
#
class FakeCursor:
    def __init__(self, state, last_query_holder):
        self.state = state
        self.last_query_holder = last_query_holder
        self._last_result = None
        self.lastrowid = None
        self.rowcount = 0

    def execute(self, query, params=None):
        q = (query or "").strip().lower()
        self.last_query_holder.append((query, params))

        # LOGIN: select password_hash, nombre_completo from bibliotecarios where usuario = %s
        if "select password_hash" in q and "from bibliotecarios" in q:
            usuario = params[0]
            row = None
            for u in self.state['bibliotecarios']:
                if u['usuario'] == usuario:
                    row = (u['password_hash'], u.get('nombre_completo'))
                    break
            self._last_result = row
            return

        # select password_hash from bibliotecarios where usuario = %s
        if "select password_hash from bibliotecarios where usuario" in q:
            usuario = params[0]
            row = None
            for u in self.state['bibliotecarios']:
                if u['usuario'] == usuario:
                    row = (u['password_hash'],)
                    break
            self._last_result = row
            return

        # update bibliotecarios set password_hash = %s where usuario = %s
        if q.startswith("update bibliotecarios set password_hash"):
            nueva_hash, usuario = params
            for u in self.state['bibliotecarios']:
                if u['usuario'] == usuario:
                    u['password_hash'] = nueva_hash
                    self.rowcount = 1
                    break
            self._last_result = None
            return

        # INSERT libros
        if q.startswith("insert into libros"):
            titulo, paginas, isbn, asignatura = params
            nid = max([r['id'] for r in self.state['libros']] + [0]) + 1
            row = {'id': nid, 'titulo': titulo, 'paginas': paginas, 'isbn': isbn, 'asignatura': asignatura}
            self.state['libros'].append(row)
            self.lastrowid = nid
            self._last_result = None
            return

        # select id from autores where nombre = %s
        if q.startswith("select id from autores where nombre"):
            nombre = params[0]
            row = None
            for a in self.state['autores']:
                if a['nombre'] == nombre:
                    row = (a['id'],)
                    break
            self._last_result = row
            return

        # insert into autores (nombre)
        if q.startswith("insert into autores"):
            nombre = params[0]
            nid = max([r['id'] for r in self.state['autores']] + [0]) + 1
            row = {'id': nid, 'nombre': nombre}
            self.state['autores'].append(row)
            self.lastrowid = nid
            self._last_result = None
            return

        # insert into libro_autor (libro_id, autor_id)
        if q.startswith("insert into libro_autor"):
            libro_id, autor_id = params
            self.state['libro_autor'].append({'libro_id': libro_id, 'autor_id': autor_id})
            self._last_result = None
            return

        # cargar libros (group_concat)
        if "select l.id, l.titulo" in q and "group_concat" in q and "from libros l" in q and "group by l.id" in q:
            resultados = []
            for l in sorted(self.state['libros'], key=lambda x: x['titulo'] or ''):
                autores = [a['nombre'] for a in self.state['autores'] if any(la['autor_id']==a['id'] and la['libro_id']==l['id'] for la in self.state['libro_autor'])]
                resultados.append({'id': l['id'], 'titulo': l['titulo'], 'paginas': l['paginas'], 'isbn': l['isbn'], 'asignatura': l['asignatura'], 'autores': '; '.join(autores) if autores else None})
            self._last_result = resultados
            return

        # buscar por titulo
        if "where l.titulo like" in q:
            term = params[0].strip('%')
            found = None
            for l in self.state['libros']:
                if term.lower() in (l['titulo'] or '').lower():
                    autores = [a['nombre'] for a in self.state['autores'] if any(la['autor_id']==a['id'] and la['libro_id']==l['id'] for la in self.state['libro_autor'])]
                    found = {'id': l['id'], 'titulo': l['titulo'], 'paginas': l['paginas'], 'isbn': l['isbn'], 'asignatura': l['asignatura'], 'autores': '; '.join(autores) if autores else None}
                    break
            self._last_result = found
            return

        # listar por autor (where a.nombre like)
        if "where a.nombre like" in q:
            term = params[0].strip('%').lower()
            resultados = []
            for l in self.state['libros']:
                autores = [a['nombre'] for a in self.state['autores'] if any(la['autor_id']==a['id'] and la['libro_id']==l['id'] for la in self.state['libro_autor'])]
                if any(term in a.lower() for a in autores):
                    resultados.append({'id': l['id'], 'titulo': l['titulo'], 'paginas': l['paginas'], 'isbn': l['isbn'], 'asignatura': l['asignatura'], 'autores': '; '.join(autores) if autores else None})
            self._last_result = resultados
            return

        # listar por asignatura (where l.asignatura like)
        if "where l.asignatura like" in q:
            term = params[0].strip('%').lower()
            resultados = []
            for l in self.state['libros']:
                if term in (l['asignatura'] or '').lower():
                    autores = [a['nombre'] for a in self.state['autores'] if any(la['autor_id']==a['id'] and la['libro_id']==l['id'] for la in self.state['libro_autor'])]
                    resultados.append({'id': l['id'], 'titulo': l['titulo'], 'paginas': l['paginas'], 'isbn': l['isbn'], 'asignatura': l['asignatura'], 'autores': '; '.join(autores) if autores else None})
            self._last_result = resultados
            return

        # delete libro by id
        if q.startswith("delete from libros where id"):
            lid = params[0]
            before = len(self.state['libros'])
            self.state['libros'] = [l for l in self.state['libros'] if l['id'] != lid]
            self.state['libro_autor'] = [la for la in self.state['libro_autor'] if la['libro_id'] != lid]
            self.rowcount = 1 if len(self.state['libros']) < before else 0
            self._last_result = None
            return

        # select autor_id from libro_autor where libro_id
        if q.startswith("select autor_id from libro_autor where libro_id"):
            lid = params[0]
            res = [(la['autor_id'],) for la in self.state['libro_autor'] if la['libro_id']==lid]
            self._last_result = res
            return

        # delete orphan authors
        if "delete a from autores a" in q and "left join libro_autor la" in q:
            before = len(self.state['autores'])
            autor_ids_with = {la['autor_id'] for la in self.state['libro_autor']}
            self.state['autores'] = [a for a in self.state['autores'] if a['id'] in autor_ids_with]
            self.rowcount = before - len(self.state['autores'])
            self._last_result = None
            return

        # select nombre from autores
        if q.startswith("select nombre from autores"):
            self._last_result = [(a['nombre'],) for a in sorted(self.state['autores'], key=lambda x: x['nombre'])]
            return

        # select id from autores where nombre = ...
        if q.startswith("select id from autores where nombre") or q.startswith("select id from autores where nombre ="):
            nombre = params[0]
            row = None
            for a in self.state['autores']:
                if a['nombre'] == nombre:
                    row = (a['id'],)
                    break
            self._last_result = row
            return

        # update libros set titulo...
        if q.startswith("update libros set titulo"):
            nuevo_titulo, nuevo_isbn, nueva_asignatura, lid = params
            for l in self.state['libros']:
                if l['id'] == lid:
                    l['titulo'] = nuevo_titulo
                    l['isbn'] = nuevo_isbn
                    l['asignatura'] = nueva_asignatura
                    self.rowcount = 1
                    break
            self._last_result = None
            return

        # delete from libro_autor where libro_id = %s
        if q.startswith("delete from libro_autor where libro_id"):
            lid = params[0]
            before = len(self.state['libro_autor'])
            self.state['libro_autor'] = [la for la in self.state['libro_autor'] if la['libro_id'] != lid]
            self.rowcount = before - len(self.state['libro_autor'])
            self._last_result = None
            return

        # fallback
        self._last_result = None

    def fetchone(self):
        return self._last_result

    def fetchall(self):
        return self._last_result or []

    def close(self):
        pass

class FakeConnection:
    def __init__(self, state):
        self.state = state
        self.last_query_holder = []
    def cursor(self, dictionary=False):
        return FakeCursor(self.state, self.last_query_holder)
    def commit(self):
        pass
    def close(self):
        pass

def fresh_state():
    return {
        'bibliotecarios':[
            {'id':1,'usuario':'admin','password_hash': hashlib.sha256('admin123'.encode()).hexdigest(),'nombre_completo':'Admin'}
        ],
        'libros':[
            {'id':1,'titulo':'Python Básico','paginas':200,'isbn':1234567890123,'asignatura':'Programación I'}
        ],
        'autores':[{'id':1,'nombre':'Juan Perez'}],
        'libro_autor':[{'libro_id':1,'autor_id':1}]
    }

def make_conn(state=None):
    if state is None:
        state = fresh_state()
    return FakeConnection(state)

#
# Monkeypatch helper fixture to inject our fake connection into biblioteca_core.crear_conexion
#
@pytest.fixture(autouse=False)
def use_fake_db(monkeypatch):
    # Not auto-applied globally — lo usaremos en cada test individual cuando convenga
    monkeypatch.setattr(core, 'crear_conexion', lambda state=None: make_conn(state) if state is None else make_conn(state))
    yield

#
# ---- Unit tests (DB-level logic) ----
#

def test_login_exitoso(monkeypatch):
    state = fresh_state()
    monkeypatch.setattr(core, 'crear_conexion', lambda: make_conn(state))
    ok, nombre = core.verificar_login_usuario('admin', 'admin123')
    assert ok and nombre == 'Admin'

def test_login_invalido(monkeypatch):
    state = fresh_state()
    monkeypatch.setattr(core, 'crear_conexion', lambda: make_conn(state))
    ok, nombre = core.verificar_login_usuario('admin', 'wrongpass')
    assert not ok and nombre is None

def test_logout_route_session(monkeypatch):
    # If app exists, test that /logout clears session and redirects (Flask test)
    if not HAS_FLASK_APP:
        pytest.skip("Flask app not available")
    client = flask_app.test_client()
    # Simulate login by setting session cookie using test_request_context + session transaction
    with flask_app.test_client() as c:
        with c.session_transaction() as sess:
            sess['usuario'] = 'admin'
        resp = c.get('/logout', follow_redirects=False)
        # logout should redirect or return 200; ensure session cleared
        with c.session_transaction() as sess2:
            assert 'usuario' not in sess2

def test_cambiar_password_exitoso(monkeypatch):
    state = fresh_state()
    conn = make_conn(state)
    monkeypatch.setattr(core, 'crear_conexion', lambda: conn)
    ok, msg = core.cambiar_password_usuario('admin', 'admin123', 'nueva123')
    assert ok and msg == "Contraseña cambiada"
    assert state['bibliotecarios'][0]['password_hash'] == hashlib.sha256('nueva123'.encode()).hexdigest()

def test_cambiar_password_actual_incorrecta(monkeypatch):
    state = fresh_state()
    monkeypatch.setattr(core, 'crear_conexion', lambda: make_conn(state))
    ok, msg = core.cambiar_password_usuario('admin', 'bad', 'nuevapw')
    assert not ok and msg == "Contraseña actual incorrecta"

def test_cambiar_password_nueva_invalida(monkeypatch):
    state = fresh_state()
    monkeypatch.setattr(core, 'crear_conexion', lambda: make_conn(state))
    ok, msg = core.cambiar_password_usuario('admin', 'admin123', 'nu')
    assert not ok and msg == "La contraseña debe tener al menos 4 caracteres"

def test_listar_libros(monkeypatch):
    state = fresh_state()
    monkeypatch.setattr(core, 'crear_conexion', lambda: make_conn(state))
    libros = core.cargar_libros()
    assert isinstance(libros, list)
    assert len(libros) == 1 and libros[0]['titulo'] == 'Python Básico'

def test_alta_libro_completa(monkeypatch):
    state = fresh_state()
    monkeypatch.setattr(core, 'crear_conexion', lambda: make_conn(state))
    ok = core.insertar_libro_dict('Nuevo Libro', ['Autor X'], 123, 9876543210123, 'Lógica')
    assert ok
    libros = core.cargar_libros()
    assert any(l['titulo']=='Nuevo Libro' for l in libros)

def test_alta_fallida(monkeypatch):
    # Simulate failure by making crear_conexion return None
    monkeypatch.setattr(core, 'crear_conexion', lambda: None)
    ok = core.insertar_libro_dict('Fail', ['A'], 10, None, 'X')
    assert not ok

def test_editar_libro(monkeypatch):
    state = fresh_state()
    monkeypatch.setattr(core, 'crear_conexion', lambda: make_conn(state))
    ok = core.modificar_libro_por_id(1, 'Python Avanzado', ['Juan Perez','Maria'], 1111111111111, 'Programación II', None)
    assert ok
    libros = core.cargar_libros()
    assert any(l['titulo']=='Python Avanzado' for l in libros)

def test_editar_libro_inexistente(monkeypatch):
    state = fresh_state()
    monkeypatch.setattr(core, 'crear_conexion', lambda: make_conn(state))
    ok = core.modificar_libro_por_id(999, 'No Existe', ['X'], None, 'Ninguna', None)
    # función puede devolver True o False dependiendo de implementación; verificamos que no haya creado id 999
    assert ok
    assert not any(l['id']==999 for l in state['libros'])

def test_eliminar_libro(monkeypatch):
    state = fresh_state()
    monkeypatch.setattr(core, 'crear_conexion', lambda: make_conn(state))
    ok = core.eliminar_libro_por_id(1)
    assert ok
    assert len(state['libros'])==0

def test_eliminar_libro_inexistente(monkeypatch):
    state = fresh_state()
    monkeypatch.setattr(core, 'crear_conexion', lambda: make_conn(state))
    ok = core.eliminar_libro_por_id(999)
    assert ok
    assert len(state['libros'])==1

def test_busqueda_por_autor_exitosa(monkeypatch):
    state = fresh_state()
    monkeypatch.setattr(core, 'crear_conexion', lambda: make_conn(state))
    libros = core.listar_libros_por_autor('Juan')
    assert isinstance(libros, list) and len(libros)>=1

def test_busqueda_por_asignatura_con_eleccion(monkeypatch):
    state = fresh_state()
    monkeypatch.setattr(core, 'crear_conexion', lambda: make_conn(state))
    libros = core.listar_libros_por_asignatura('Programación I')
    assert isinstance(libros, list) and len(libros)>=1

def test_listado_exitoso(monkeypatch):
    state = fresh_state()
    monkeypatch.setattr(core, 'crear_conexion', lambda: make_conn(state))
    autores = core.listar_autores_db()
    assert isinstance(autores, list) and 'Juan Perez' in autores

def test_listado_vacio(monkeypatch):
    state = {'bibliotecarios':[], 'libros':[], 'autores':[], 'libro_autor':[]}
    monkeypatch.setattr(core, 'crear_conexion', lambda: make_conn(state))
    autores = core.listar_autores_db()
    assert autores == []
