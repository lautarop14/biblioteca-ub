#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from flask import Flask, render_template, request, redirect, url_for, flash, session
import os
import biblioteca_core as core  # importa tus funciones modulares

app = Flask(__name__)
app.secret_key = os.getenv('FLASK_SECRET', 'cambiame_en_produccion')

# Crear tablas si no existen (opcional: se ejecuta al iniciar)
core.crear_tablas()

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
        ok, nombre = core.verificar_login_usuario(usuario, password)
        if ok:
            session['logged_in'] = True
            session['usuario'] = usuario
            session['nombre'] = nombre
            flash(f'Bienvenido/a, {nombre}', 'success')
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
def menu():
    if not session.get('logged_in'):
        return redirect(url_for('login'))
    return render_template('menu.html')

@app.route('/libros')
def listar_libros():
    if not session.get('logged_in'):
        return redirect(url_for('login'))
    libros = core.cargar_libros()
    return render_template('libros.html', libros=libros)

@app.route('/buscar', methods=['GET','POST'])
def buscar():
    if not session.get('logged_in'):
        return redirect(url_for('login'))
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
def nuevo_libro():
    if not session.get('logged_in'):
        return redirect(url_for('login'))
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
def editar_libro(libro_id):
    if not session.get('logged_in'):
        return redirect(url_for('login'))
    if request.method == 'POST':
        titulo = request.form.get('titulo','').strip()
        autores_input = request.form.get('autores','').strip()
        isbn = request.form.get('isbn') or None
        asignatura = request.form.get('asignatura','').strip()
        autores = [a.strip() for a in autores_input.split(';') if a.strip()]
        ok = core.modificar_libro_por_id(libro_id, titulo, autores, isbn, asignatura)
        if ok:
            flash('Libro modificado.', 'success')
            return redirect(url_for('listar_libros'))
        else:
            flash('Error al modificar libro.', 'danger')
    libro = core.buscar_libro_por_titulo_by_id = None
    # Cargar datos del libro por id
    libro = None
    # Reutilizamos la consulta existente: hacer SELECT por id
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
def eliminar_libro(libro_id):
    if not session.get('logged_in'):
        return redirect(url_for('login'))
    ok = core.eliminar_libro_por_id(libro_id)
    if ok:
        flash('Libro eliminado.', 'success')
    else:
        flash('Error al eliminar libro.', 'danger')
    return redirect(url_for('listar_libros'))

@app.route('/autores')
def listar_autores():
    if not session.get('logged_in'):
        return redirect(url_for('login'))
    
    # Forzar limpieza de autores huérfanos antes de mostrar
    core.limpiar_todos_autores_huerfanos()
    
    autores = core.listar_autores_db()
    return render_template('autores.html', autores=autores)

@app.route('/buscar/titulo', methods=['GET','POST'])
def buscar_titulo():
    if not session.get('logged_in'):
        return redirect(url_for('login'))
    libro = None
    if request.method == 'POST':
        titulo = request.form.get('titulo','').strip()
        libro = core.buscar_libro_por_titulo(titulo)
        if not libro:
            flash('Libro no encontrado.', 'warning')
    return render_template('buscar_titulo.html', libro=libro)

@app.route('/buscar/autor', methods=['GET','POST'])
def buscar_autor():
    if not session.get('logged_in'):
        return redirect(url_for('login'))
    libros = []  # Cambiar de libros_por_autor a libros
    if request.method == 'POST':
        autor = request.form.get('autor','').strip()
        libros = core.listar_libros_por_autor(autor)  # Ahora devuelve lista completa
        if not libros:
            flash('No se encontraron libros de ese autor.', 'warning')
    return render_template('buscar_autor.html', libros=libros)  # Cambiar aquí

@app.route('/buscar/asignatura', methods=['GET','POST'])
def buscar_asignatura():
    if not session.get('logged_in'):
        return redirect(url_for('login'))
    libros = []  # Cambiar de libros_por_asignatura a libros
    if request.method == 'POST':
        asign = request.form.get('asignatura','').strip()
        libros = core.listar_libros_por_asignatura(asign)  # Ahora devuelve lista completa
        if not libros:
            flash('No se encontraron libros de esa asignatura.', 'warning')
    return render_template('buscar_asignatura.html', libros=libros)  # Cambiar aquí

@app.route('/cambiar_password', methods=['GET','POST'])
def cambiar_password():
    if not session.get('logged_in'):
        return redirect(url_for('login'))
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

# Agrega esto temporalmente en app.py después de importar core
@app.route('/limpiar_autores')
def limpiar_autores():
    if not session.get('logged_in'):
        return redirect(url_for('login'))
    eliminados = core.limpiar_autores_huerfanos()
    flash(f'Se eliminaron {eliminados} autores huérfanos', 'success')
    return redirect(url_for('listar_autores'))

if __name__ == '__main__':
    app.run(debug=True)
