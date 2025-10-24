#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import mysql.connector
from mysql.connector import Error
import hashlib

# Configuración de la base de datos (ajustá si es necesario)
DB_CONFIG = {
    'host': 'localhost',
    'user': 'usuario_biblioteca',
    'password': 'password123',
    'database': 'biblioteca_db',
    'port': 3306
}

def crear_conexion():
    try:
        conexion = mysql.connector.connect(**DB_CONFIG)
        if conexion.is_connected():
            return conexion
    except Error as e:
        print(f"Error al conectar a MySQL: {e}")
        return None

def crear_tablas():
    conexion = crear_conexion()
    if conexion:
        try:
            cursor = conexion.cursor()
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS bibliotecarios (
                    id INT AUTO_INCREMENT PRIMARY KEY,
                    usuario VARCHAR(50) UNIQUE NOT NULL,
                    password_hash VARCHAR(255) NOT NULL,
                    nombre_completo VARCHAR(100) NOT NULL,
                    fecha_creacion TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """)
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS libros (
                    id INT AUTO_INCREMENT PRIMARY KEY,
                    titulo VARCHAR(255) NOT NULL,
                    paginas INT,
                    isbn BIGINT,
                    asignatura VARCHAR(255),
                    UNIQUE KEY unique_isbn (isbn)
                )
            """)
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS autores (
                    id INT AUTO_INCREMENT PRIMARY KEY,
                    nombre VARCHAR(255) NOT NULL UNIQUE
                )
            """)
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS libro_autor (
                    libro_id INT,
                    autor_id INT,
                    PRIMARY KEY (libro_id, autor_id),
                    FOREIGN KEY (libro_id) REFERENCES libros(id) ON DELETE CASCADE,
                    FOREIGN KEY (autor_id) REFERENCES autores(id) ON DELETE CASCADE
                )
            """)
            cursor.execute("SELECT COUNT(*) FROM bibliotecarios")
            if cursor.fetchone()[0] == 0:
                pw = hashlib.sha256("admin123".encode()).hexdigest()
                cursor.execute(
                    "INSERT INTO bibliotecarios (usuario, password_hash, nombre_completo) VALUES (%s, %s, %s)",
                    ("admin", pw, "Administrador Principal")
                )
            
            # Limpiar autores huérfanos que puedan existir desde el inicio
            cursor.execute("""
                DELETE a FROM autores a
                LEFT JOIN libro_autor la ON a.id = la.autor_id
                WHERE la.autor_id IS NULL
            """)
            
            conexion.commit()
            cursor.close()
            conexion.close()
            return True
        except Error as e:
            print(f"Error al crear tablas: {e}")
            try:
                cursor.close()
            except:
                pass
            conexion.close()
            return False
    return False

# FUNCIONES DE LÓGICA (adaptadas para uso programático)

def cargar_libros():
    libros = []
    conexion = crear_conexion()
    if conexion:
        try:
            cursor = conexion.cursor(dictionary=True)
            cursor.execute("""
                SELECT l.id, l.titulo, l.paginas, l.isbn, l.asignatura,
                       GROUP_CONCAT(a.nombre SEPARATOR '; ') as autores
                FROM libros l
                LEFT JOIN libro_autor la ON l.id = la.libro_id
                LEFT JOIN autores a ON la.autor_id = a.id
                GROUP BY l.id
                ORDER BY l.titulo
            """)
            resultados = cursor.fetchall()
            for libro in resultados:
                autores = libro['autores'].split('; ') if libro['autores'] else []
                libros.append({
                    'id': libro['id'],
                    'titulo': libro['titulo'],
                    'autor': autores,
                    'autores': libro['autores'] or '',
                    'paginas': libro['paginas'],
                    'isbn': libro['isbn'],
                    'asignatura': libro['asignatura'] or ''
                })
        except Error as e:
            print(f"Error al cargar libros: {e}")
        finally:
            cursor.close()
            conexion.close()
    return libros

def obtener_autor_id(nombre_autor):
    conexion = crear_conexion()
    if conexion:
        try:
            cursor = conexion.cursor()
            cursor.execute("SELECT id FROM autores WHERE nombre = %s", (nombre_autor,))
            resultado = cursor.fetchone()
            if resultado:
                id_ = resultado[0]
                cursor.close()
                conexion.close()
                return id_
            else:
                cursor.execute("INSERT INTO autores (nombre) VALUES (%s)", (nombre_autor,))
                conexion.commit()
                last = cursor.lastrowid
                cursor.close()
                conexion.close()
                return last
        except Error as e:
            print(f"Error al obtener/crear autor: {e}")
            try:
                cursor.close()
            except:
                pass
            conexion.close()
            return None
    return None

def insertar_libro_dict(titulo, autores_list, paginas=None, isbn=None, asignatura=''):
    conexion = crear_conexion()
    if conexion:
        try:
            cursor = conexion.cursor()
            cursor.execute(
                "INSERT INTO libros (titulo, paginas, isbn, asignatura) VALUES (%s, %s, %s, %s)",
                (titulo, paginas, isbn, asignatura)
            )
            libro_id = cursor.lastrowid
            for nombre in autores_list:
                autor_id = obtener_autor_id(nombre)
                if autor_id:
                    cursor.execute(
                        "INSERT INTO libro_autor (libro_id, autor_id) VALUES (%s, %s)",
                        (libro_id, autor_id)
                    )
            conexion.commit()
            cursor.close()
            conexion.close()
            return True
        except Error as e:
            print(f"Error al insertar libro: {e}")
            try:
                conexion.rollback()
                cursor.close()
            except:
                pass
            conexion.close()
            return False
    return False

def buscar_libro_por_titulo(titulo_parcial):
    conexion = crear_conexion()
    if conexion:
        try:
            cursor = conexion.cursor(dictionary=True)
            cursor.execute("""
                SELECT l.id, l.titulo, l.paginas, l.isbn, l.asignatura,
                       GROUP_CONCAT(a.nombre SEPARATOR '; ') as autores
                FROM libros l
                LEFT JOIN libro_autor la ON l.id = la.libro_id
                LEFT JOIN autores a ON la.autor_id = a.id
                WHERE l.titulo LIKE %s
                GROUP BY l.id
                LIMIT 1
            """, (f'%{titulo_parcial}%',))
            libro = cursor.fetchone()
            cursor.close()
            conexion.close()
            return libro
        except Error as e:
            print(f"Error al buscar libro: {e}")
            try:
                cursor.close()
            except:
                pass
            conexion.close()
            return None
    return None

def eliminar_libro_por_id(libro_id):
    conexion = crear_conexion()
    if conexion:
        try:
            cursor = conexion.cursor()
            
            print(f"Eliminando libro ID: {libro_id}")
            
            # PRIMERO: obtener los autores asociados a este libro
            cursor.execute("SELECT autor_id FROM libro_autor WHERE libro_id = %s", (libro_id,))
            autores_asociados = [row[0] for row in cursor.fetchall()]
            print(f"Autores asociados al libro: {autores_asociados}")
            
            # SEGUNDO: eliminar el libro (esto elimina automáticamente las relaciones en libro_autor por CASCADE)
            cursor.execute("DELETE FROM libros WHERE id = %s", (libro_id,))
            print("Libro eliminado de la tabla libros")
            
            conexion.commit()
            cursor.close()
            conexion.close()
            
            # TERCERO: limpiar todos los autores huérfanos después de eliminar
            limpiar_todos_autores_huerfanos()
            
            print(f"Libro {libro_id} eliminado exitosamente")
            return True
        except Error as e:
            print(f"Error al eliminar libro: {e}")
            try:
                conexion.rollback()
                cursor.close()
            except:
                pass
            conexion.close()
            return False
    return False

def limpiar_todos_autores_huerfanos():
    """Limpia todos los autores huérfanos de la base de datos"""
    conexion = crear_conexion()
    if conexion:
        try:
            cursor = conexion.cursor()
            
            # Método más robusto para MySQL
            cursor.execute("""
                DELETE a FROM autores a
                LEFT JOIN libro_autor la ON a.id = la.autor_id
                WHERE la.autor_id IS NULL
            """)
            
            eliminados = cursor.rowcount
            conexion.commit()
            cursor.close()
            conexion.close()
            print(f"Autores huérfanos eliminados: {eliminados}")
            return eliminados
        except Error as e:
            print(f"Error al limpiar autores huérfanos: {e}")
            try:
                cursor.close()
            except:
                pass
            conexion.close()
            return 0
    return 0

def modificar_libro_por_id(libro_id, nuevo_titulo, nuevos_autores_list, nuevo_isbn=None, nueva_asignatura=''):
    conexion = crear_conexion()
    if conexion:
        try:
            cursor = conexion.cursor()
            
            # PRIMERO: obtener los autores antiguos ANTES de eliminar las relaciones
            cursor.execute("SELECT autor_id FROM libro_autor WHERE libro_id = %s", (libro_id,))
            autores_antiguos = [row[0] for row in cursor.fetchall()]
            
            # Actualizar libro
            cursor.execute(
                "UPDATE libros SET titulo = %s, isbn = %s, asignatura = %s WHERE id = %s",
                (nuevo_titulo, nuevo_isbn, nueva_asignatura, libro_id)
            )
            
            # Eliminar relaciones antiguas
            cursor.execute("DELETE FROM libro_autor WHERE libro_id = %s", (libro_id,))
            
            # Crear nuevas relaciones
            nuevos_autores_ids = []
            for nombre in nuevos_autores_list:
                cursor.execute("SELECT id FROM autores WHERE nombre = %s", (nombre,))
                r = cursor.fetchone()
                if r:
                    autor_id = r[0]
                else:
                    cursor.execute("INSERT INTO autores (nombre) VALUES (%s)", (nombre,))
                    autor_id = cursor.lastrowid
                cursor.execute("INSERT INTO libro_autor (libro_id, autor_id) VALUES (%s, %s)", (libro_id, autor_id))
                nuevos_autores_ids.append(autor_id)
            
            # Eliminar autores huérfanos (los que estaban antes pero no están en los nuevos)
            autores_eliminados = 0
            for autor_id_antiguo in autores_antiguos:
                if autor_id_antiguo not in nuevos_autores_ids:
                    cursor.execute("""
                        SELECT COUNT(*) FROM libro_autor 
                        WHERE autor_id = %s
                    """, (autor_id_antiguo,))
                    count = cursor.fetchone()[0]
                    if count == 0:
                        cursor.execute("DELETE FROM autores WHERE id = %s", (autor_id_antiguo,))
                        autores_eliminados += 1
            
            conexion.commit()
            cursor.close()
            conexion.close()
            print(f"Libro {libro_id} modificado. Autores eliminados: {autores_eliminados}")
            return True
        except Error as e:
            print(f"Error al modificar libro: {e}")
            try:
                conexion.rollback()
                cursor.close()
            except:
                pass
            conexion.close()
            return False
    return False

def listar_autores_db():
    # Primero limpiar autores huérfanos antes de listar
    limpiar_todos_autores_huerfanos()
    
    conexion = crear_conexion()
    autores = []
    if conexion:
        try:
            cursor = conexion.cursor()
            cursor.execute("SELECT nombre FROM autores ORDER BY nombre")
            autores = [a[0] for a in cursor.fetchall()]
            cursor.close()
            conexion.close()
        except Error as e:
            print(f"Error al listar autores: {e}")
            try:
                cursor.close()
            except:
                pass
            conexion.close()
    return autores

def listar_libros_por_autor(autor_parcial):
    conexion = crear_conexion()
    libros = []
    if conexion:
        try:
            cursor = conexion.cursor(dictionary=True)
            cursor.execute("""
                SELECT l.id, l.titulo, l.paginas, l.isbn, l.asignatura,
                       GROUP_CONCAT(a.nombre SEPARATOR '; ') as autores
                FROM libros l
                JOIN libro_autor la ON l.id = la.libro_id
                JOIN autores a ON a.id = la.autor_id
                WHERE a.nombre LIKE %s
                GROUP BY l.id
                ORDER BY l.titulo
            """, (f'%{autor_parcial}%',))
            resultados = cursor.fetchall()
            for libro in resultados:
                autores = libro['autores'].split('; ') if libro['autores'] else []
                libros.append({
                    'id': libro['id'],
                    'titulo': libro['titulo'],
                    'autor': autores,
                    'autores': libro['autores'] or '',
                    'paginas': libro['paginas'],
                    'isbn': libro['isbn'],
                    'asignatura': libro['asignatura'] or ''
                })
            cursor.close()
            conexion.close()
        except Error as e:
            print(f"Error al listar por autor: {e}")
            try:
                cursor.close()
            except:
                pass
            conexion.close()
    return libros

def listar_libros_por_asignatura(asignatura_parcial):
    conexion = crear_conexion()
    libros = []
    if conexion:
        try:
            cursor = conexion.cursor(dictionary=True)
            cursor.execute("""
                SELECT l.id, l.titulo, l.paginas, l.isbn, l.asignatura,
                       GROUP_CONCAT(a.nombre SEPARATOR '; ') as autores
                FROM libros l
                LEFT JOIN libro_autor la ON l.id = la.libro_id
                LEFT JOIN autores a ON a.id = la.autor_id
                WHERE l.asignatura LIKE %s
                GROUP BY l.id
                ORDER BY l.titulo
            """, (f'%{asignatura_parcial}%',))
            resultados = cursor.fetchall()
            for libro in resultados:
                autores = libro['autores'].split('; ') if libro['autores'] else []
                libros.append({
                    'id': libro['id'],
                    'titulo': libro['titulo'],
                    'autor': autores,
                    'autores': libro['autores'] or '',
                    'paginas': libro['paginas'],
                    'isbn': libro['isbn'],
                    'asignatura': libro['asignatura'] or ''
                })
            cursor.close()
            conexion.close()
        except Error as e:
            print(f"Error al listar por asignatura: {e}")
            try:
                cursor.close()
            except:
                pass
            conexion.close()
    return libros

def verificar_login_usuario(usuario, password):
    conexion = crear_conexion()
    if conexion:
        try:
            cursor = conexion.cursor()
            cursor.execute("SELECT password_hash, nombre_completo FROM bibliotecarios WHERE usuario = %s", (usuario,))
            row = cursor.fetchone()
            cursor.close(); conexion.close()
            if row:
                password_hash_db, nombre = row
                if hashlib.sha256(password.encode()).hexdigest() == password_hash_db:
                    return True, nombre
            return False, None
        except Error as e:
            print(f"Error al verificar login: {e}")
            try:
                cursor.close()
            except:
                pass
            conexion.close()
            return False, None

def cambiar_password_usuario(usuario_actual, password_actual, nueva_password):
    conexion = crear_conexion()
    if conexion:
        try:
            cursor = conexion.cursor()
            cursor.execute("SELECT password_hash FROM bibliotecarios WHERE usuario = %s", (usuario_actual,))
            row = cursor.fetchone()
            if not row:
                cursor.close(); conexion.close(); return False, "Usuario no encontrado"
            if hashlib.sha256(password_actual.encode()).hexdigest() != row[0]:
                cursor.close(); conexion.close(); return False, "Contraseña actual incorrecta"
            nueva_hash = hashlib.sha256(nueva_password.encode()).hexdigest()
            cursor.execute("UPDATE bibliotecarios SET password_hash=%s WHERE usuario=%s", (nueva_hash, usuario_actual))
            conexion.commit()
            cursor.close(); conexion.close()
            return True, "Contraseña cambiada"
        except Error as e:
            print(f"Error al cambiar contraseña: {e}")
            try:
                conexion.rollback(); cursor.close()
            except:
                pass
            conexion.close()
            return False, str(e)
        
def obtener_asignaturas():
    """Devuelve la lista predefinida de asignaturas de la carrera"""
    asignaturas = [
        "Programación I",
        "Lógica",
        "Sistemas en la Empresa",
        "Organización de Computadoras",
        "Programación II",
        "Matemática Discreta",
        "Requisitos de Software",
        "Sistemas Operativos",
        "Programación III",
        "Testeo y Prueba de Software",
        "Base de Datos",
        "Elementos de Computación en Red",
        "Proyecto de Construcción de Software",
        "Programación de Base de Datos",
        "Seguridad Informática",
        "Programación en Ambiente de Redes"
    ]
    return asignaturas
