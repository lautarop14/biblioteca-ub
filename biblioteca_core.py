#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import mysql.connector
from mysql.connector import Error
import hashlib
from datetime import datetime, timedelta

# Configuración de la base de datos
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
            
            # Crear tablas
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS bibliotecarios (
                    id INT AUTO_INCREMENT PRIMARY KEY,
                    usuario VARCHAR(50) UNIQUE NOT NULL,
                    password_hash VARCHAR(255) NOT NULL,
                    nombre_completo VARCHAR(100) NOT NULL,
                    fecha_creacion TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    admin BOOLEAN NOT NULL DEFAULT FALSE
                )
            """)
            
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS libros (
                    id INT AUTO_INCREMENT PRIMARY KEY,
                    titulo VARCHAR(255) NOT NULL,
                    paginas INT,
                    isbn BIGINT,
                    asignatura VARCHAR(255),
                    disponible BOOLEAN DEFAULT TRUE
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
            
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS prestamos (
                    id INT AUTO_INCREMENT PRIMARY KEY,
                    libro_id INT NOT NULL,
                    usuario_bibliotecario VARCHAR(50) NOT NULL,
                    usuario_id INT NOT NULL,
                    fecha_prestamo TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    fecha_devolucion_estimada DATE,
                    fecha_devolucion_real DATE,
                    estado ENUM('activo', 'devuelto') NOT NULL DEFAULT 'activo',
                    FOREIGN KEY (libro_id) REFERENCES libros(id) ON DELETE CASCADE,
                    FOREIGN KEY (usuario_id) REFERENCES bibliotecarios(id) ON DELETE CASCADE
                )
            """)
                        
            # Crear usuario admin con admin=True si no existe
            cursor.execute("SELECT COUNT(*) FROM bibliotecarios WHERE usuario = 'admin'")
            if cursor.fetchone()[0] == 0:
                pw = hashlib.sha256("admin123".encode()).hexdigest()
                cursor.execute(
                    "INSERT INTO bibliotecarios (usuario, password_hash, nombre_completo, admin) VALUES (%s, %s, %s, %s)",
                    ("admin", pw, "Administrador Principal", True)
                )
                print("Usuario admin creado con admin=True")

            # Limpiar autores huérfanos que puedan existir desde el inicio
            try:
                cursor.execute("""
                    DELETE a FROM autores a
                    LEFT JOIN libro_autor la ON a.id = la.autor_id
                    WHERE la.autor_id IS NULL
                """)
            except Error as e:
                print(f"Nota: No se pudieron limpiar autores huérfanos: {e}")

            conexion.commit()
            cursor.close()
            conexion.close()
            print("Tablas creadas/verificadas exitosamente")
            return True
        except Error as e:
            print(f"Error al crear tablas: {e}")
            try:
                conexion.rollback()
                cursor.close()
            except:
                pass
            conexion.close()
            return False
    return False

# FUNCIONES PARA LIBROS
def cargar_libros():
    libros = []
    conexion = crear_conexion()
    if conexion:
        try:
            cursor = conexion.cursor(dictionary=True)
            cursor.execute("""
                SELECT l.id, l.titulo, l.paginas, l.isbn, l.asignatura, l.disponible,
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
                    'asignatura': libro['asignatura'] or '',
                    'disponible': libro['disponible']
                })
        except Error as e:
            print(f"Error al cargar libros: {e}")
        finally:
            cursor.close()
            conexion.close()
    return libros

def cargar_libros_con_disponibilidad():
    """Carga libros incluyendo información de disponibilidad"""
    return cargar_libros()  # Ya incluye disponibilidad

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
    libros = []
    if conexion:
        try:
            cursor = conexion.cursor(dictionary=True)
            cursor.execute("""
                SELECT l.id, l.titulo, l.paginas, l.isbn, l.asignatura, l.disponible,
                       GROUP_CONCAT(a.nombre SEPARATOR '; ') as autores
                FROM libros l
                LEFT JOIN libro_autor la ON l.id = la.libro_id
                LEFT JOIN autores a ON la.autor_id = a.id
                WHERE l.titulo LIKE %s
                GROUP BY l.id
                ORDER BY l.titulo
            """, (f'%{titulo_parcial}%',))
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
                    'asignatura': libro['asignatura'] or '',
                    'disponible': libro['disponible']
                })
            cursor.close()
            conexion.close()
        except Error as e:
            print(f"Error al buscar libro: {e}")
            try:
                cursor.close()
            except:
                pass
            conexion.close()
    return libros

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

def modificar_libro_por_id(libro_id, nuevo_titulo, nuevos_autores_list, nuevo_isbn=None, nueva_asignatura='', nuevas_paginas=None):
    conexion = crear_conexion()
    if conexion:
        try:
            cursor = conexion.cursor()
            # Obtener los autores antiguos ANTES de eliminar las relaciones
            cursor.execute("SELECT autor_id FROM libro_autor WHERE libro_id = %s", (libro_id,))
            autores_antiguos = [row[0] for row in cursor.fetchall()]

            # Actualizar libro
            cursor.execute(
                "UPDATE libros SET titulo = %s, paginas = %s, isbn = %s, asignatura = %s WHERE id = %s",
                (nuevo_titulo, nuevas_paginas, nuevo_isbn, nueva_asignatura, libro_id)
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

            # Eliminar autores huérfanos
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
                SELECT l.id, l.titulo, l.paginas, l.isbn, l.asignatura, l.disponible,
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
                    'asignatura': libro['asignatura'] or '',
                    'disponible': libro['disponible']
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
                SELECT l.id, l.titulo, l.paginas, l.isbn, l.asignatura, l.disponible,
                       GROUP_CONCAT(a.nombre SEPARATOR '; ') as autores
                FROM libros l
                LEFT JOIN libro_autor la ON l.id = la.libro_id
                LEFT JOIN autores a ON a.id = la.autor_id
                WHERE l.asignatura = %s
                GROUP BY l.id
                ORDER BY l.titulo
            """, (f'{asignatura_parcial}',))
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
                    'asignatura': libro['asignatura'] or '',
                    'disponible': libro['disponible']
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

# FUNCIONES DE USUARIOS 
def verificar_login_usuario(usuario, password):
    conexion = crear_conexion()
    if conexion:
        try:
            cursor = conexion.cursor()
            cursor.execute("SELECT password_hash, id, nombre_completo, admin FROM bibliotecarios WHERE usuario = %s", (usuario,))
            row = cursor.fetchone()
            cursor.close(); conexion.close()
            if row:
                password_hash_db, usuario_id, nombre, admin = row
                if hashlib.sha256(password.encode()).hexdigest() == password_hash_db:
                    # Convertir admin boolean a string 'admin' o 'lector'
                    rol = 'admin' if admin else 'lector'
                    return True, usuario_id, nombre, rol
            return False, None, None, None
        except Error as e:
            print(f"Error al verificar login: {e}")
            try:
                cursor.close()
            except:
                pass
            conexion.close()
            return False, None, None, None
            
def cambiar_password_usuario(usuario_actual, password_actual, nueva_password):
    if len(nueva_password.strip()) < 4:
        return False, "La contraseña debe tener al menos 4 caracteres"
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

# FUNCIONES PARA PRÉSTAMOS Y DEVOLUCIONES
def solicitar_prestamo(libro_id, usuario_solicitante, usuario_id):
    """Solicita un préstamo"""
    conexion = crear_conexion()
    if conexion:
        try:
            cursor = conexion.cursor()

            # Verificar que el libro esté disponible
            cursor.execute("SELECT disponible FROM libros WHERE id = %s", (libro_id,))
            libro = cursor.fetchone()

            if not libro:
                cursor.close()
                conexion.close()
                return False, "Libro no encontrado"

            if not libro[0]:  # Si no está disponible
                cursor.close()
                conexion.close()
                return False, "El libro no está disponible para préstamo"

            cursor.execute("SELECT DATE_ADD(CURDATE(), INTERVAL 30 DAY)")
            fecha_devolucion_estimada = cursor.fetchone()[0]

            cursor.execute("""
                INSERT INTO prestamos (libro_id, usuario_bibliotecario, usuario_id,
                                    fecha_prestamo, fecha_devolucion_estimada, estado)
                VALUES (%s, %s, %s, CURDATE(), %s, 'activo')
            """, (libro_id, usuario_solicitante, usuario_id, fecha_devolucion_estimada))

            cursor.execute("UPDATE libros SET disponible = FALSE WHERE id = %s", (libro_id,))

            conexion.commit()
            prestamo_id = cursor.lastrowid
            cursor.close()
            conexion.close()

            return True, f"Solicitud de préstamo registrada. El libro podrá ser retirado dentro de los siguientes 3 días hábiles."

        except Error as e:
            print(f"Error al solicitar préstamo: {e}")
            try:
                conexion.rollback()
                cursor.close()
            except:
                pass
            conexion.close()
            return False, f"Error en el sistema: {e}"
    return False, "Error de conexión a la base de datos"
    
def registrar_devolucion(libro_id):
    """Registra la devolución de un libro (solo admin)"""
    conexion = crear_conexion()
    if conexion:
        try:
            cursor = conexion.cursor()
            
            # Verificar que el libro esté prestado
            cursor.execute("SELECT disponible FROM libros WHERE id = %s", (libro_id,))
            libro = cursor.fetchone()
            
            if not libro:
                cursor.close()
                conexion.close()
                return False, "Libro no encontrado"
            
            if libro[0]:  # Si ya está disponible
                cursor.close()
                conexion.close()
                return False, "El libro ya está disponible"
            
            cursor.execute("""
                SELECT id, estado FROM prestamos 
                WHERE libro_id = %s AND estado = 'activo'
                ORDER BY fecha_prestamo DESC LIMIT 1
            """, (libro_id,))
            prestamo = cursor.fetchone()
            
            if not prestamo:
                cursor.close()
                conexion.close()
                return False, "No se encontró préstamo activo para este libro"
            
            prestamo_id, estado = prestamo
            
            cursor.execute("""
                UPDATE prestamos 
                SET estado = 'devuelto', fecha_devolucion_real = CURDATE()
                WHERE id = %s
            """, (prestamo_id,))
            
            cursor.execute("UPDATE libros SET disponible = TRUE WHERE id = %s", (libro_id,))
            
            conexion.commit()
            cursor.close()
            conexion.close()
            
            return True, "Devolución registrada exitosamente. Libro disponible para nuevos préstamos."
            
        except Error as e:
            print(f"Error al registrar devolución: {e}")
            try:
                conexion.rollback()
                cursor.close()
            except:
                pass
            conexion.close()
            return False, f"Error en el sistema: {e}"
    return False, "Error de conexión a la base de datos"

def obtener_prestamos_activos():
    """Obtiene todos los préstamos activos"""
    conexion = crear_conexion()
    prestamos = []
    if conexion:
        try:
            cursor = conexion.cursor(dictionary=True)
            cursor.execute("""
                SELECT p.id, p.libro_id, l.titulo, p.usuario_id, b.usuario,
                    p.fecha_prestamo, p.fecha_devolucion_estimada, p.estado,
                    GROUP_CONCAT(a.nombre SEPARATOR '; ') as autores
                FROM prestamos p
                JOIN libros l ON p.libro_id = l.id
                JOIN bibliotecarios b ON p.usuario_id = b.id
                LEFT JOIN libro_autor la ON l.id = la.libro_id
                LEFT JOIN autores a ON la.autor_id = a.id
                WHERE p.estado='activo'
                GROUP BY p.id
                ORDER BY p.fecha_devolucion_estimada
            """)
            prestamos = cursor.fetchall()
            cursor.close()
            conexion.close()
        except Error as e:
            print(f"Error al obtener préstamos activos: {e}")
            try:
                cursor.close()
            except:
                pass
            conexion.close()
    return prestamos

# FUNCIONES PARA LISTA DE USUARIOS

def crear_usuario_lector(usuario, nombre_completo, password):
    """Crea un nuevo usuario lector"""
    if len(password.strip()) < 4:
        return False, "La contraseña debe tener al menos 4 caracteres"
    
    conexion = crear_conexion()
    if conexion:
        try:
            cursor = conexion.cursor()
            
            # Verificar si el usuario ya existe
            cursor.execute("SELECT COUNT(*) FROM bibliotecarios WHERE usuario = %s", (usuario,))
            if cursor.fetchone()[0] > 0:
                cursor.close()
                conexion.close()
                return False, "El usuario ya existe"
            
            password_hash = hashlib.sha256(password.encode()).hexdigest()
            cursor.execute(
                "INSERT INTO bibliotecarios (usuario, password_hash, nombre_completo, admin) VALUES (%s, %s, %s, %s)",
                (usuario, password_hash, nombre_completo, False)
            )
            
            conexion.commit()
            cursor.close()
            conexion.close()
            return True, f"Usuario '{usuario}' creado exitosamente (lector)"
            
        except Error as e:
            print(f"Error al crear usuario: {e}")
            try:
                conexion.rollback()
                cursor.close()
            except:
                pass
            conexion.close()
            return False, f"Error en el sistema: {e}"
    return False, "Error de conexión a la base de datos"

def listar_usuarios():
    """Lista todos los usuarios"""
    conexion = crear_conexion()
    usuarios = []
    if conexion:
        try:
            cursor = conexion.cursor(dictionary=True)
            cursor.execute("""
                SELECT id, usuario, nombre_completo, admin, fecha_creacion 
                FROM bibliotecarios 
                ORDER BY admin DESC, usuario
            """)
            usuarios = cursor.fetchall()
            cursor.close()
            conexion.close()
        except Error as e:
            print(f"Error al listar usuarios: {e}")
            try:
                cursor.close()
            except:
                pass
            conexion.close()
    return usuarios

def eliminar_usuario(usuario_id):
    """Elimina un usuario (solo no-admins)"""
    conexion = crear_conexion()
    if conexion:
        try:
            cursor = conexion.cursor()
            
            # Verificar que no sea admin y que exista
            cursor.execute("SELECT usuario, admin FROM bibliotecarios WHERE id = %s", (usuario_id,))
            usuario = cursor.fetchone()
            
            if not usuario:
                cursor.close()
                conexion.close()
                return False, "Usuario no encontrado"
            
            if usuario[1]:  # Si admin=True
                cursor.close()
                conexion.close()
                return False, "No se pueden eliminar usuarios administradores"
            
            cursor.execute("DELETE FROM bibliotecarios WHERE id = %s", (usuario_id,))
            conexion.commit()
            
            cursor.close()
            conexion.close()
            return True, f"Usuario '{usuario[0]}' eliminado exitosamente"
            
        except Error as e:
            print(f"Error al eliminar usuario: {e}")
            try:
                conexion.rollback()
                cursor.close()
            except:
                pass
            conexion.close()
            return False, f"Error en el sistema: {e}"
    return False, "Error de conexión a la base de datos"
