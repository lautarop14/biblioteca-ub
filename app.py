#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from flask import Flask, render_template, request, redirect, url_for, flash, session
from functools import wraps
import os
import biblioteca_core as core

app = Flask(__name__)
app.secret_key = os.getenv('FLASK_SECRET', 'cambiame_en_produccion')

core.crear_tablas()

# ===== DECORADORES PARA CONTROL DE ACCESO =====
def admin_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not session.get('logged_in'):
            flash('Debe iniciar sesión', 'danger')
            return redirect(url_for('login'))
        if session.get('rol') != 'admin':
            flash('Acceso denegado. Se requiere rol de administrador', 'danger')
            return redirect(url_for('menu'))
        return f(*args, **kwargs)
    return decorated_function

def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not session.get('logged_in'):
            flash('Debe iniciar sesión', 'danger')
            return redirect(url_for('login'))
        return f(*args, **kwargs)
    return decorated_function

@app.route('/')
def home():
    if session.get('logged_in'):
        return redirect(url_for('menu'))
    return redirect(url_for('login'))

@app.route('/login', methods=['GET','POST'])
def login():
    if request.method == 'POST':
        usuario = request.form.get('usuario','').strip()
        password = request.form.get('password','')
        ok, nombre, rol = core.verificar_login_usuario(usuario, password)
        if ok:
            session['logged_in'] = True
            session['usuario'] = usuario
            session['nombre'] = nombre
            session['rol'] = rol
            flash(f'Bienvenido/a, {nombre} ({rol})', 'success')
            return redirect(url_for('menu'))
        else:
            flash('Usuario o contraseña inválidos', 'danger')
    return render_template('login.html')

@app.route('/logout')
def logout():
    session.clear()
    flash('Sesión cerrada', 'info')
    return redirect(url_for('login'))

@app.route('/menu')
@login_required
def menu():
    return render_template('menu.html')

@app.route('/libros')
@login_required
def listar_libros():
    libros = core.cargar_libros_con_disponibilidad() 
    return render_template('libros.html', libros=libros)

@app.route('/buscar', methods=['GET','POST'])
@login_required
def buscar():
    libro = None
    libros_por_autor = None
    libros_por_asignatura = None
    if request.method == 'POST':
        if 'titulo' in request.form:
            titulo = request.form.get('titulo','').strip()
            libro = core.buscar_libro_por_titulo(titulo)
            if not libro:
                flash('Libro no encontrado.', 'warning')
        elif 'autor' in request.form:
            autor = request.form.get('autor','').strip()
            libros_por_autor = core.listar_libros_por_autor(autor)
            if not libros_por_autor:
                flash('No se encontraron libros de ese autor.', 'warning')
        elif 'asignatura' in request.form:
            asign = request.form.get('asignatura','').strip()
            libros_por_asignatura = core.listar_libros_por_asignatura(asign)
            if not libros_por_asignatura:
                flash('No se encontraron libros de esa asignatura.', 'warning')
    return render_template('buscar.html', libro=libro, libros_por_autor=libros_por_autor, libros_por_asignatura=libros_por_asignatura)

@app.route('/libros/nuevo', methods=['GET','POST'])
@admin_required
def nuevo_libro():
    if request.method == 'POST':
        titulo = request.form.get('titulo','').strip()
        autores_input = request.form.get('autores','').strip()
        paginas = request.form.get('paginas') or None
        isbn = request.form.get('isbn') or None
        asignatura = request.form.get('asignatura','').strip()
        autores = [a.strip() for a in autores_input.split(';') if a.strip()]
        ok = core.insertar_libro_dict(titulo, autores, paginas, isbn, asignatura)
        if ok:
            flash('Libro agregado correctamente.', 'success')
            return redirect(url_for('listar_libros'))
        else:
            flash('Error al agregar libro.', 'danger')
    return render_template('form_libro.html', libro=None)

@app.route('/libros/editar/<int:libro_id>', methods=['GET','POST'])
@admin_required
def editar_libro(libro_id):
    if request.method == 'POST':
        titulo = request.form.get('titulo','').strip()
        autores_input = request.form.get('autores','').strip()
        isbn = request.form.get('isbn') or None
        asignatura = request.form.get('asignatura','').strip()
        autores = [a.strip() for a in autores_input.split(';') if a.strip()]
        paginas = request.form.get('paginas') or None
        ok = core.modificar_libro_por_id(libro_id, titulo, autores, isbn, asignatura, paginas)
        if ok:
            flash('Libro modificado.', 'success')
            return redirect(url_for('listar_libros'))
        else:
            flash('Error al modificar libro.', 'danger')
    # Cargar datos del libro por id
    libro = None

    conn = core.crear_conexion()
    if conn:
        cur = conn.cursor(dictionary=True)
        cur.execute("""
            SELECT l.id, l.titulo, l.paginas, l.isbn, l.asignatura,
                   GROUP_CONCAT(a.nombre SEPARATOR '; ') AS autores
            FROM libros l
            LEFT JOIN libro_autor la ON la.libro_id = l.id
            LEFT JOIN autores a ON a.id = la.autor_id
            WHERE l.id = %s
            GROUP BY l.id
        """, (libro_id,))
        libro = cur.fetchone()
        cur.close(); conn.close()
    if not libro:
        flash('Libro no encontrado.', 'warning')
        return redirect(url_for('listar_libros'))
    return render_template('form_libro.html', libro=libro)

@app.route('/libros/eliminar/<int:libro_id>', methods=['POST'])
@admin_required
def eliminar_libro(libro_id):
    ok = core.eliminar_libro_por_id(libro_id)
    if ok:
        flash('Libro eliminado.', 'success')
    else:
        flash('Error al eliminar libro.', 'danger')
    return redirect(url_for('listar_libros'))

@app.route('/autores')
@login_required
def listar_autores():
    # Forzar limpieza de autores huérfanos antes de mostrar
    core.limpiar_todos_autores_huerfanos()

    autores = core.listar_autores_db()
    return render_template('autores.html', autores=autores)

@app.route('/buscar/titulo', methods=['GET','POST'])
@login_required
def buscar_titulo():
    libros = []
    if request.method == 'POST':
        titulo = request.form.get('titulo','').strip()
        libros = core.buscar_libro_por_titulo(titulo)
        if not libros:
            flash('Libro no encontrado.', 'warning')
    return render_template('buscar_titulo.html', libros=libros)

@app.route('/buscar/autor', methods=['GET','POST'])
@login_required
def buscar_autor():
    libros = []
    if request.method == 'POST':
        autor = request.form.get('autor','').strip()
        libros = core.listar_libros_por_autor(autor)
        if not libros:
            flash('No se encontraron libros de ese autor.', 'warning')
    return render_template('buscar_autor.html', libros=libros)

@app.route('/buscar/asignatura', methods=['GET','POST'])
@login_required
def buscar_asignatura():
    libros = []
    if request.method == 'POST':
        asign = request.form.get('asignatura','').strip()
        libros = core.listar_libros_por_asignatura(asign)
        if not libros:
            flash('No se encontraron libros de esa asignatura.', 'warning')
    return render_template('buscar_asignatura.html', libros=libros)

@app.route('/cambiar_password', methods=['GET','POST'])
@login_required
def cambiar_password():
    usuario = session.get('usuario')
    if request.method == 'POST':
        actual = request.form.get('password_actual','')
        nueva = request.form.get('nueva_password','')
        confirmar = request.form.get('confirmar_password','')
        if nueva != confirmar:
            flash('Las contraseñas no coinciden.', 'danger'); return render_template('cambiar_password.html')
        if len(nueva) < 4:
            flash('La contraseña debe tener al menos 4 caracteres.', 'danger'); return render_template('cambiar_password.html')
        ok, msg = core.cambiar_password_usuario(usuario, actual, nueva)
        if ok:
            flash(msg, 'success')
            return redirect(url_for('logout'))
        else:
            flash(msg, 'danger')
    return render_template('cambiar_password.html')

@app.route('/limpiar_autores')
@admin_required
def limpiar_autores():
    eliminados = core.limpiar_autores_huerfanos()
    flash(f'Se eliminaron {eliminados} autores huérfanos', 'success')
    return redirect(url_for('listar_autores'))

# ===== RUTAS PARA PRÉSTAMOS Y DEVOLUCIONES (ACTUALIZADAS) =====

@app.route('/libros/solicitar_prestamo/<int:libro_id>', methods=['GET', 'POST'])
@login_required
def solicitar_prestamo(libro_id):
    """Solicitar un préstamo (disponible para todos los usuarios logueados)"""
    # Obtener información del libro
    conexion = core.crear_conexion()
    libro = None
    if conexion:
        cur = conexion.cursor(dictionary=True)
        cur.execute("""
            SELECT l.id, l.titulo, l.disponible,
                   GROUP_CONCAT(a.nombre SEPARATOR '; ') AS autores
            FROM libros l
            LEFT JOIN libro_autor la ON la.libro_id = l.id
            LEFT JOIN autores a ON a.id = la.autor_id
            WHERE l.id = %s
            GROUP BY l.id
        """, (libro_id,))
        libro = cur.fetchone()
        cur.close()
        conexion.close()
    
    if not libro:
        flash('Libro no encontrado', 'danger')
        return redirect(url_for('listar_libros'))
    
    if request.method == 'POST':
        usuario = session.get('usuario')
        ok, mensaje = core.solicitar_prestamo(libro_id, usuario)
        if ok:
            flash(mensaje, 'success')
            return redirect(url_for('listar_libros'))
        else:
            flash(mensaje, 'danger')
    
    return render_template('solicitar_prestamo.html', libro=libro)

@app.route('/libros/registrar_devolucion/<int:libro_id>', methods=['GET', 'POST'])
@admin_required
def registrar_devolucion(libro_id):
    """Registrar devolución de un libro (SOLO ADMIN)"""
    # Obtener información del libro
    conexion = core.crear_conexion()
    libro = None
    if conexion:
        cur = conexion.cursor(dictionary=True)
        cur.execute("""
            SELECT l.id, l.titulo, l.disponible,
                   GROUP_CONCAT(a.nombre SEPARATOR '; ') AS autores
            FROM libros l
            LEFT JOIN libro_autor la ON la.libro_id = l.id
            LEFT JOIN autores a ON a.id = la.autor_id
            WHERE l.id = %s
            GROUP BY l.id
        """, (libro_id,))
        libro = cur.fetchone()
        cur.close()
        conexion.close()
    
    if not libro:
        flash('Libro no encontrado', 'danger')
        return redirect(url_for('listar_libros'))
    
    if request.method == 'POST':
        # El admin puede registrar la devolución
        ok, mensaje = core.registrar_devolucion(libro_id)
        if ok:
            flash(mensaje, 'success')
            return redirect(url_for('listar_prestamos'))
        else:
            flash(mensaje, 'danger')
    
    return render_template('registrar_devolucion.html', libro=libro)

@app.route('/prestamos')
@login_required
def listar_prestamos():
    prestamos = core.obtener_prestamos_activos()
    return render_template('prestamos.html', prestamos=prestamos)

# ===== RUTAS PARA GESTIÓN DE USUARIOS (SOLO ADMIN) =====

@app.route('/usuarios')
@admin_required
def listar_usuarios():
    usuarios = core.listar_usuarios()
    return render_template('usuarios.html', usuarios=usuarios)

@app.route('/usuarios/nuevo', methods=['GET','POST'])
@admin_required
def nuevo_usuario():
    if request.method == 'POST':
        usuario = request.form.get('usuario','').strip()
        nombre_completo = request.form.get('nombre_completo','').strip()
        password = request.form.get('password','')
        confirmar_password = request.form.get('confirmar_password','')
        
        if password != confirmar_password:
            flash('Las contraseñas no coinciden', 'danger')
            return render_template('form_usuario.html')
        
        ok, mensaje = core.crear_usuario_lector(usuario, nombre_completo, password)
        if ok:
            flash(mensaje, 'success')
            return redirect(url_for('listar_usuarios'))
        else:
            flash(mensaje, 'danger')
    
    return render_template('form_usuario.html')

@app.route('/usuarios/eliminar/<int:usuario_id>', methods=['POST'])
@admin_required
def eliminar_usuario(usuario_id):
    ok, mensaje = core.eliminar_usuario(usuario_id)
    if ok:
        flash(mensaje, 'success')
    else:
        flash(mensaje, 'danger')
    return redirect(url_for('listar_usuarios'))

@app.route('/libros/confirmar_prestamo/<int:libro_id>', methods=['GET', 'POST'])
@admin_required
def confirmar_prestamo(libro_id):
    """Confirmar que el libro fue retirado físicamente (solo ADMIN)"""
    # Obtener información del libro
    conexion = core.crear_conexion()
    libro = None
    if conexion:
        cur = conexion.cursor(dictionary=True)
        cur.execute("""
            SELECT l.id, l.titulo, l.disponible,
                   GROUP_CONCAT(a.nombre SEPARATOR '; ') AS autores
            FROM libros l
            LEFT JOIN libro_autor la ON la.libro_id = l.id
            LEFT JOIN autores a ON a.id = la.autor_id
            WHERE l.id = %s
            GROUP BY l.id
        """, (libro_id,))
        libro = cur.fetchone()
        cur.close()
        conexion.close()
    
    if not libro:
        flash('Libro no encontrado', 'danger')
        return redirect(url_for('listar_libros'))
    
    if request.method == 'POST':
        ok, mensaje = core.confirmar_prestamo(libro_id)
        if ok:
            flash(mensaje, 'success')
            return redirect(url_for('listar_prestamos'))
        else:
            flash(mensaje, 'danger')
    
    return render_template('confirmar_prestamo.html', libro=libro)

if __name__ == '__main__':
    app.run(debug=True, port=5000)