# test_busqueda_libros.py
import hashlib
import pytest
import biblioteca_core as core

# --- Fake DB simple ---
class FakeCursor:
    def __init__(self, state):
        self.state = state
        self._last_result = None

    def execute(self, query, params=None):
        q = (query or "").lower()
        term = params[0].strip('%').lower()
        # buscar por titulo
        if "where l.titulo like" in q:
            found = []
            for l in self.state['libros']:
                if term in (l['titulo'] or '').lower():
                    autores = [a['nombre'] for a in self.state['autores'] 
                               if any(la['autor_id']==a['id'] and la['libro_id']==l['id'] 
                                      for la in self.state['libro_autor'])]
                    found.append({'id': l['id'], 'titulo': l['titulo'], 'paginas': l['paginas'],
                                  'isbn': l['isbn'], 'asignatura': l['asignatura'],
                                  'autores': '; '.join(autores) if autores else None})
            self._last_result = found
        # listar por autor
        elif "where a.nombre like" in q:
            res = []
            for l in self.state['libros']:
                autores = [a['nombre'] for a in self.state['autores'] 
                           if any(la['autor_id']==a['id'] and la['libro_id']==l['id'] 
                                  for la in self.state['libro_autor'])]
                if any(term in a.lower() for a in autores):
                    res.append({'id': l['id'], 'titulo': l['titulo'], 'paginas': l['paginas'],
                                'isbn': l['isbn'], 'asignatura': l['asignatura'],
                                'autores': '; '.join(autores) if autores else None})
            self._last_result = res
        # listar por asignatura
        elif "where l.asignatura like" in q:
            res = []
            for l in self.state['libros']:
                if term in (l['asignatura'] or '').lower():
                    autores = [a['nombre'] for a in self.state['autores'] 
                               if any(la['autor_id']==a['id'] and la['libro_id']==l['id'] 
                                      for la in self.state['libro_autor'])]
                    res.append({'id': l['id'], 'titulo': l['titulo'], 'paginas': l['paginas'],
                                'isbn': l['isbn'], 'asignatura': l['asignatura'],
                                'autores': '; '.join(autores) if autores else None})
            self._last_result = res
        else:
            self._last_result = []

    def fetchall(self):
        return self._last_result or []

    def close(self):
        pass

class FakeConnection:
    def __init__(self, state):
        self.state = state
    def cursor(self, dictionary=False):
        return FakeCursor(self.state)
    def close(self):
        pass

def fresh_state():
    return {
        'libros':[{'id':1,'titulo':'Python Básico','paginas':200,'isbn':1234567890123,'asignatura':'Programación'}],
        'autores':[{'id':1,'nombre':'Juan Perez'}],
        'libro_autor':[{'libro_id':1,'autor_id':1}]
    }

@pytest.fixture
def fake_db(monkeypatch):
    state = fresh_state()
    monkeypatch.setattr(core, 'crear_conexion', lambda: FakeConnection(state))
    return state

# --- Tests ---
def test_busqueda_por_titulo_exitosa(fake_db):
    libro = core.buscar_libro_por_titulo('Python')
    assert len(libro) == 1
    assert libro[0]['titulo'] == 'Python Básico'

def test_busqueda_por_titulo_no_exitosa(fake_db):
    libro = core.buscar_libro_por_titulo('NoExiste')
    assert libro == []

def test_busqueda_por_autor_no_exitosa(fake_db):
    libros = core.listar_libros_por_autor('AutorNunca')
    assert libros == []

def test_busqueda_por_asignatura_no_exitosa(fake_db):
    libros = core.listar_libros_por_asignatura('NoAsign')
    assert libros == []
