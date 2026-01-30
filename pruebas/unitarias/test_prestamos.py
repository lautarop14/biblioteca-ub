import sys
import os
import pytest
from unittest.mock import patch, MagicMock

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

import biblioteca_core as core

@pytest.fixture
def mock_db():
    with patch("biblioteca_core.crear_conexion") as mock_conexion:
        mock_conn = MagicMock()
        mock_cursor = MagicMock()

        mock_conexion.return_value = mock_conn
        mock_conn.cursor.return_value = mock_cursor

        yield mock_cursor

def test_prestamo_libro_disponible(mock_db):
    # Libro disponible + fecha devolución
    mock_db.fetchone.side_effect = [
        (True,),          # libro disponible
        ("2025-01-01",)   # fecha devolución estimada
    ]

    ok, mensaje = core.solicitar_prestamo(1, "usuario_test")

    assert ok is True
    assert "Solicitud de préstamo registrada" in mensaje

def test_prestamo_libro_prestado(mock_db):
    # Libro NO disponible
    mock_db.fetchone.return_value = (False,)

    ok, mensaje = core.solicitar_prestamo(1, "usuario_test")

    assert ok is False
    assert mensaje == "El libro no está disponible para préstamo"

def test_devolver_libro_prestado(mock_db):
    mock_db.fetchone.side_effect = [
        (False,),          # libro no disponible
        (1, "activo")      # préstamo activo
    ]

    ok, mensaje = core.registrar_devolucion(1)

    assert ok is True
    assert "Devolución registrada exitosamente" in mensaje

def test_devolver_libro_disponible(mock_db):
    # Libro ya disponible
    mock_db.fetchone.return_value = (True,)

    ok, mensaje = core.registrar_devolucion(1)

    assert ok is False
    assert mensaje == "El libro ya está disponible"
