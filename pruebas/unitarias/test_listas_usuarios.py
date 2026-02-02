#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import pytest
import sys
import os

# Añadir el directorio actual al path para importar biblioteca_core
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from biblioteca_core import (
    crear_usuario_lector,
    eliminar_usuario,
    listar_usuarios,
    obtener_prestamos_activos,
    cargar_libros,
    crear_tablas,
    crear_conexion
)

# ===== FIXTURES PARA CONFIGURACIÓN =====

@pytest.fixture(scope="session", autouse=True)
def setup_database():
    """Configura la base de datos antes de todas las pruebas"""
    print("\n=== Configurando base de datos para pruebas ===")
    crear_tablas()
    yield
    print("\n=== Pruebas completadas ===")

@pytest.fixture
def limpiar_usuarios():
    """Limpia usuarios de prueba antes y después de cada prueba"""
    # Limpiar usuarios antes de la prueba
    conn = crear_conexion()
    if conn:
        cursor = conn.cursor()
        # Eliminar todos los usuarios excepto 'admin'
        cursor.execute("DELETE FROM bibliotecarios WHERE usuario != 'admin'")
        conn.commit()
        cursor.close()
        conn.close()
    yield
    # Limpiar usuarios después de la prueba
    conn = crear_conexion()
    if conn:
        cursor = conn.cursor()
        cursor.execute("DELETE FROM bibliotecarios WHERE usuario != 'admin'")
        conn.commit()
        cursor.close()
        conn.close()

@pytest.fixture
def limpiar_libros():
    """Limpia libros de prueba antes y después de cada prueba"""
    # Limpiar libros antes de la prueba
    conn = crear_conexion()
    if conn:
        cursor = conn.cursor()
        cursor.execute("DELETE FROM libros")
        cursor.execute("DELETE FROM autores")
        conn.commit()
        cursor.close()
        conn.close()
    yield
    # Limpiar libros después de la prueba
    conn = crear_conexion()
    if conn:
        cursor = conn.cursor()
        cursor.execute("DELETE FROM libros")
        cursor.execute("DELETE FROM autores")
        conn.commit()
        cursor.close()
        conn.close()

# ===== PRUEBAS PARA GESTIÓN DE USUARIOS =====

class TestGestionUsuarios:
    """Pruebas unitarias para la gestión de usuarios (Casos A7, A8, A10, A11, A13)"""
    
    # A7: Agregar usuario lector
    def test_a7_agregar_usuario_lector(self, limpiar_usuarios):
        """Prueba A7: Agregar usuario lector exitosamente"""
        print("\n--- Ejecutando prueba A7: Agregar usuario lector ---")
        
        # Datos de prueba
        usuario = "lector_prueba"
        nombre = "Lector de Prueba"
        password = "lector123"
        
        # Ejecutar la función
        resultado, mensaje = crear_usuario_lector(usuario, nombre, password)
        
        # Verificaciones
        assert resultado is True, f"El usuario debería haberse creado. Error: {mensaje}"
        assert "creado exitosamente" in mensaje.lower(), f"Mensaje inesperado: {mensaje}"
        assert "lector" in mensaje.lower(), "El usuario debería ser de tipo lector"
        
        # Verificar que efectivamente se creó
        conn = crear_conexion()
        cursor = conn.cursor(dictionary=True)
        cursor.execute("SELECT * FROM bibliotecarios WHERE usuario = %s", (usuario,))
        usuario_db = cursor.fetchone()
        cursor.close()
        conn.close()
        
        assert usuario_db is not None, "El usuario no se encontró en la base de datos"
        assert usuario_db['usuario'] == usuario
        assert usuario_db['nombre_completo'] == nombre
        assert usuario_db['admin'] == 0  # Debería ser False (lector)
        
        print(f"✓ Usuario '{usuario}' creado exitosamente")
    
    # A8: Agregar usuario lector inválido
    def test_a8_agregar_usuario_lector_invalido(self, limpiar_usuarios):
        """Prueba A8: Intentar agregar usuario lector con contraseña inválida"""
        print("\n--- Ejecutando prueba A8: Agregar usuario lector inválido ---")
        
        # Crear primero un usuario válido
        usuario1 = "lector_valido"
        crear_usuario_lector(usuario1, "Usuario Válido", "valid123")
        
        # Caso 1: Usuario duplicado
        resultado_duplicado, mensaje_duplicado = crear_usuario_lector(usuario1, "Otro Nombre", "nueva123")
        
        assert resultado_duplicado is False, "No debería permitir usuarios duplicados"
        assert "ya existe" in mensaje_duplicado.lower(), f"Mensaje inesperado: {mensaje_duplicado}"
        
        # Caso 2: Contraseña demasiado corta
        resultado_corta, mensaje_corta = crear_usuario_lector("nuevo_usuario", "Nombre", "123")
        
        assert resultado_corta is False, "No debería aceptar contraseñas de menos de 4 caracteres"
        assert "al menos 4 caracteres" in mensaje_corta.lower(), f"Mensaje inesperado: {mensaje_corta}"
        
        # Caso 3: Datos vacíos
        resultado_vacio, mensaje_vacio = crear_usuario_lector("", "", "")
        
        assert resultado_vacio is False, "No debería aceptar datos vacíos"
        
        print("✓ Validaciones de usuario inválido funcionan correctamente")
    
    # A10: Eliminar usuario lector
    def test_a10_eliminar_usuario_lector(self, limpiar_usuarios):
        """Prueba A10: Eliminar usuario lector exitosamente"""
        print("\n--- Ejecutando prueba A10: Eliminar usuario lector ---")
        
        # Primero crear un usuario para eliminar
        usuario = "lector_a_eliminar"
        nombre = "Usuario a Eliminar"
        password = "pass1234"
        
        crear_usuario_lector(usuario, nombre, password)
        
        # Obtener el ID del usuario recién creado
        conn = crear_conexion()
        cursor = conn.cursor(dictionary=True)
        cursor.execute("SELECT id FROM bibliotecarios WHERE usuario = %s", (usuario,))
        usuario_db = cursor.fetchone()
        cursor.close()
        conn.close()
        
        usuario_id = usuario_db['id']
        
        # Ejecutar eliminación
        resultado, mensaje = eliminar_usuario(usuario_id)
        
        # Verificaciones
        assert resultado is True, f"Debería eliminar el usuario. Error: {mensaje}"
        assert "eliminado exitosamente" in mensaje.lower(), f"Mensaje inesperado: {mensaje}"
        assert usuario in mensaje, f"El mensaje debería contener el nombre de usuario"
        
        # Verificar que ya no existe
        conn = crear_conexion()
        cursor = conn.cursor(dictionary=True)
        cursor.execute("SELECT * FROM bibliotecarios WHERE usuario = %s", (usuario,))
        usuario_eliminado = cursor.fetchone()
        cursor.close()
        conn.close()
        
        assert usuario_eliminado is None, "El usuario debería haber sido eliminado"
        
        print(f"✓ Usuario '{usuario}' eliminado exitosamente")
    
    # A11: Eliminar usuario lector inexistente
    def test_a11_eliminar_usuario_lector_inexistente(self, limpiar_usuarios):
        """Prueba A11: Intentar eliminar usuario lector que no existe"""
        print("\n--- Ejecutando prueba A11: Eliminar usuario lector inexistente ---")
        
        # Intentar eliminar un ID que no existe
        id_inexistente = 99999
        
        resultado, mensaje = eliminar_usuario(id_inexistente)
        
        # Verificaciones
        assert resultado is False, "No debería eliminar un usuario inexistente"
        assert "no encontrado" in mensaje.lower() or "no existe" in mensaje.lower(), \
               f"Mensaje inesperado: {mensaje}"
        
        print("✓ Validación de usuario inexistente funciona correctamente")
    
    # A13: Lista de usuarios
    def test_a13_lista_de_usuarios(self, limpiar_usuarios):
        """Prueba A13: Listar usuarios exitosamente"""
        print("\n--- Ejecutando prueba A13: Lista de usuarios ---")
        
        # Crear varios usuarios de prueba
        usuarios_prueba = [
            ("lector1", "Lector Uno", "pass1"),
            ("lector2", "Lector Dos", "pass2"),
            ("lector3", "Lector Tres", "pass3")
        ]
        
        for usuario, nombre, password in usuarios_prueba:
            crear_usuario_lector(usuario, nombre, password)
        
        # Obtener lista de usuarios
        usuarios = listar_usuarios()
        
        # Verificaciones
        assert isinstance(usuarios, list), "Debería devolver una lista"
        assert len(usuarios) >= 4, f"Debería haber al menos 4 usuarios (admin + 3 lectores). Encontrados: {len(usuarios)}"
        
        # Verificar que están los usuarios esperados
        usuarios_encontrados = [u['usuario'] for u in usuarios]
        
        # Verificar admin existe
        assert any(u['usuario'] == 'admin' for u in usuarios), "Admin debería estar en la lista"
        
        # Verificar usuarios de prueba
        for usuario, _, _ in usuarios_prueba:
            assert any(u['usuario'] == usuario for u in usuarios), \
                   f"Usuario {usuario} debería estar en la lista"
        
        # Verificar estructura de datos
        for usuario in usuarios:
            assert 'id' in usuario
            assert 'usuario' in usuario
            assert 'nombre_completo' in usuario
            assert 'admin' in usuario
            assert 'fecha_creacion' in usuario
        
        print(f"✓ Listado de usuarios exitoso. Encontrados: {len(usuarios)} usuarios")

# ===== PRUEBAS PARA GESTIÓN DE PRÉSTAMOS =====

class TestGestionPrestamos:
    """Pruebas unitarias para la gestión de préstamos (Casos L16, L17)"""
    
    # L16: Lista de préstamos activos con datos
    def test_l16_lista_prestamos_activos_con_datos(self, limpiar_usuarios, limpiar_libros):
        """Prueba L16: Listar préstamos activos cuando hay datos"""
        print("\n--- Ejecutando prueba L16: Lista de préstamos activos con datos ---")
        
        # Crear un usuario lector para las pruebas
        crear_usuario_lector("prestamo_user", "Usuario Préstamo", "pass123")
        
        # Crear un libro de prueba
        conn = crear_conexion()
        cursor = conn.cursor()
        
        # Insertar libro
        cursor.execute("""
            INSERT INTO libros (titulo, paginas, isbn, asignatura, disponible)
            VALUES (%s, %s, %s, %s, %s)
        """, ("Libro para Préstamo", 200, 1234567890123, "Programación", False))
        
        libro_id = cursor.lastrowid
        
        # Insertar autor
        cursor.execute("INSERT INTO autores (nombre) VALUES (%s)", ("Autor Préstamo",))
        autor_id = cursor.lastrowid
        
        # Relacionar libro-autor
        cursor.execute("INSERT INTO libro_autor (libro_id, autor_id) VALUES (%s, %s)", 
                      (libro_id, autor_id))
        
        # Crear préstamo activo
        cursor.execute("""
            INSERT INTO prestamos (libro_id, usuario_bibliotecario, 
                                 fecha_prestamo, fecha_devolucion_estimada, estado)
            VALUES (%s, %s, CURDATE(), DATE_ADD(CURDATE(), INTERVAL 3 DAY), 'activo')
        """, (libro_id, "prestamo_user"))
        
        conn.commit()
        cursor.close()
        conn.close()
        
        # Obtener préstamos activos
        prestamos = obtener_prestamos_activos()
        
        # Verificaciones
        assert isinstance(prestamos, list), "Debería devolver una lista"
        assert len(prestamos) > 0, "Debería haber al menos un préstamo activo"
        
        for prestamo in prestamos:
            assert 'id' in prestamo
            assert 'libro_id' in prestamo
            assert 'titulo' in prestamo
            assert 'usuario_bibliotecario' in prestamo
            assert 'fecha_prestamo' in prestamo
            assert 'fecha_devolucion_estimada' in prestamo
            assert 'estado' in prestamo
            assert prestamo['estado'] in ['reservado', 'activo'], \
                   f"Estado inválido: {prestamo['estado']}"
        
        print(f"✓ Listado de préstamos activos exitoso. Encontrados: {len(prestamos)} préstamos")
    
    # L17: Lista de préstamos activos vacía
    def test_l17_lista_prestamos_activos_vacia(self, limpiar_libros):
        """Prueba L17: Listar préstamos activos cuando no hay datos"""
        print("\n--- Ejecutando prueba L17: Lista de préstamos activos vacía ---")
        
        # Limpiar préstamos existentes
        conn = crear_conexion()
        cursor = conn.cursor()
        cursor.execute("DELETE FROM prestamos")
        conn.commit()
        cursor.close()
        conn.close()
        
        # Obtener préstamos activos
        prestamos = obtener_prestamos_activos()
        
        # Verificaciones
        assert isinstance(prestamos, list), "Debería devolver una lista"
        assert len(prestamos) == 0, f"Debería devolver lista vacía. Encontrados: {len(prestamos)}"
        
        print("✓ Listado de préstamos activos vacío funciona correctamente")

# ===== PRUEBAS PARA GESTIÓN DE LIBROS =====

class TestGestionLibros:
    """Pruebas unitarias para la gestión de libros (Caso L18)"""
    
    # L18: Lista de libros vacía
    def test_l18_lista_de_libros_vacia(self, limpiar_libros):
        """Prueba L18: Listar libros cuando no hay datos"""
        print("\n--- Ejecutando prueba L18: Lista de libros vacía ---")
        
        # Obtener lista de libros
        libros = cargar_libros()
        
        # Verificaciones
        assert isinstance(libros, list), "Debería devolver una lista"
        assert len(libros) == 0, f"Debería devolver lista vacía. Encontrados: {len(libros)}"
        
        print("✓ Listado de libros vacío funciona correctamente")

# ===== PRUEBA ADICIONAL: Lista de libros con datos =====

    def test_lista_de_libros_con_datos(self, limpiar_libros):
        """Prueba adicional: Listar libros cuando hay datos"""
        print("\n--- Prueba adicional: Lista de libros con datos ---")
        
        # Crear algunos libros de prueba
        conn = crear_conexion()
        cursor = conn.cursor()
        
        # Insertar varios libros
        libros_prueba = [
            ("Python Básico", 300, 1111111111111, "Programación I", True),
            ("Python Avanzado", 400, 2222222222222, "Programación II", False),
            ("Base de Datos", 350, 3333333333333, "Base de Datos", True)
        ]
        
        for titulo, paginas, isbn, asignatura, disponible in libros_prueba:
            cursor.execute("""
                INSERT INTO libros (titulo, paginas, isbn, asignatura, disponible)
                VALUES (%s, %s, %s, %s, %s)
            """, (titulo, paginas, isbn, asignatura, disponible))
        
        conn.commit()
        cursor.close()
        conn.close()
        
        # Obtener lista de libros
        libros = cargar_libros()
        
        # Verificaciones
        assert isinstance(libros, list), "Debería devolver una lista"
        assert len(libros) == len(libros_prueba), \
               f"Debería haber {len(libros_prueba)} libros. Encontrados: {len(libros)}"
        
        for libro in libros:
            assert 'id' in libro
            assert 'titulo' in libro
            assert 'autores' in libro
            assert 'disponible' in libro
        
        print(f"✓ Listado de libros con datos exitoso. Encontrados: {len(libros)} libros")

# ===== FUNCIÓN PRINCIPAL PARA EJECUCIÓN MANUAL =====

if __name__ == "__main__":
    print("=== Ejecutando pruebas unitarias manualmente ===\n")
    
    # Ejecutar cada prueba manualmente
    test = TestGestionUsuarios()
    test_suite = [
        ("A7", test.test_a7_agregar_usuario_lector),
        ("A8", test.test_a8_agregar_usuario_lector_invalido),
        ("A10", test.test_a10_eliminar_usuario_lector),
        ("A11", test.test_a11_eliminar_usuario_lector_inexistente),
        ("A13", test.test_a13_lista_de_usuarios),
    ]
    
    for nombre_prueba, funcion_prueba in test_suite:
        try:
            print(f"\n{'='*60}")
            print(f"Ejecutando prueba: {nombre_prueba}")
            print('='*60)
            
            # Configurar base de datos
            crear_tablas()
            
            # Ejecutar prueba
            funcion_prueba()
            
            print(f"✓ Prueba {nombre_prueba} PASÓ exitosamente")
            
        except Exception as e:
            print(f"✗ Prueba {nombre_prueba} FALLÓ: {str(e)}")
    
    print("\n=== Todas las pruebas completadas ===")
