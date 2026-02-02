# 📚 Sistema de Biblioteca UB

Sistema de gestión bibliotecaria desarrollado en Python con Flask y MySQL para la Tecnicatura en Programación.

## 🚀 Características

- ✅ Gestión completa de libros y autores
- 🔍 Búsqueda por título, autor y asignatura  
- 👥 Sistema de autenticación de bibliotecarios
- 🎨 Interfaz web moderna y responsive
- 📚 Asignaturas predefinidas de la carrera
- 🔒 Cambio de contraseñas seguro

## 🛠️ Tecnologías

- **Backend**: Python + Flask
- **Base de datos**: MySQL
- **Frontend**: HTML5 + CSS3
- **Autenticación**: SHA-256

## 📋 Requisitos Previos

- Python 3.8+
- MySQL 5.7+
- pip (gestor de paquetes de Python)

## ⚡ Instalación Rápida

### 1. Clonar el repositorio
```bash
git clone https://github.com/lautarop14/biblioteca-ub.git
cd biblioteca-ub/proyecto_biblioteca
2. Configurar la base de datos
sql
-- Conectarse a MySQL como root o administrador y ejecutar:
SOURCE database/scriptbiblioteca.sql
3. Instalar dependencias de Python
bash
pip install -r requirements.txt
4. Configurar variables de entorno
bash
# Copiar el archivo de ejemplo
cp .env.example .env

# Editar el archivo .env con tus credenciales de MySQL
# (Usar editor de texto como Notepad++, VS Code, etc.)
5. Configurar el archivo .env
Edita el archivo .env con tu configuración de MySQL:

env
DB_HOST=localhost
DB_USER=tu_usuario_mysql
DB_PASSWORD=tu_password_mysql
DB_NAME=biblioteca_db
FLASK_SECRET=clave-muy-segura-para-flask
6. Ejecutar la aplicación
bash
python3 app.py
7. Acceder al sistema
Abrir en el navegador: http://localhost:5000

🔐 Credenciales por Defecto
Usuario: admin

Contraseña: admin123

⚠️ IMPORTANTE: Cambia estas credenciales en producción desde el menú "Cambiar contraseña".

🗃️ Estructura del Proyecto
text
proyecto_biblioteca/
├── app.py                 # Aplicación principal Flask
├── biblioteca_core.py     # Lógica de negocio y base de datos
├── config.py             # Configuración de la aplicación
├── requirements.txt      # Dependencias de Python
├── .env.example         # Variables de entorno de ejemplo
├── .gitignore           # Archivos ignorados por Git
├── README.md           # Este archivo
├── database/
│   └── scriptbiblioteca.sql  # Esquema y datos de la BD
├── static/
│   └── styles.css       # Estilos CSS
└── templates/
    ├── layout.html      # Plantilla base
    ├── menu.html        # Menú principal
    ├── login.html       # Inicio de sesión
    ├── libros.html      # Lista de libros
    ├── form_libro.html  # Formulario de libros
    ├── autores.html     # Lista de autores
    ├── buscar_titulo.html    # Búsqueda por título
    ├── buscar_autor.html     # Búsqueda por autor
    ├── buscar_asignatura.html # Búsqueda por asignatura
    └── cambiar_password.html  # Cambio de contraseña
📊 Asignaturas Disponibles
El sistema incluye las 16 asignaturas de la Tecnicatura en Programación:

Programación I

Lógica

Sistemas en la Empresa

Organización de Computadoras

Programación II

Matemática Discreta

Requisitos de Software

Sistemas Operativos

Programación III

Testeo y Prueba de Software

Base de Datos

Elementos de Computación en Red

Proyecto de Construcción de Software

Programación de Base de Datos

Seguridad Informática

Programación en Ambiente de Redes

🚀 Uso del Sistema
Iniciar sesión con las credenciales de administrador (admin / admin123)

Navegar por el menú para acceder a las diferentes funciones

Gestionar libros:

"Mostrar libros": Ver todos los libros

"Dar de alta libro": Agregar nuevo libro

Editar o eliminar libros desde la lista

Solicitar préstamos de libros disponibles y devolverlos

Buscar información:

"Buscar por título": Encontrar libros por nombre

"Buscar por autor": Libros de un autor específico

"Buscar por asignatura": Libros por materia

Ver préstamos activos en el momento

Administrar:

"Listar autores": Ver todos los autores

"Cambiar contraseña": Actualizar credenciales

Cerrar sesión cuando termines

Agregar y eliminar usuarios lectores/no administradores

🔧 Configuración Avanzada
Base de Datos MySQL
El script database/scriptbiblioteca.sql crea:

Base de datos biblioteca_db

Tablas: bibliotecarios, libros, autores, libro_autor, prestamos

Usuario administrador por defecto

Usuario lector por defecto

Variables de Entorno (.env)
env
# Configuración MySQL
DB_HOST=localhost
DB_USER=tu_usuario_mysql
DB_PASSWORD=tu_password_mysql
DB_NAME=biblioteca_db
DB_PORT=3306

# Seguridad Flask
FLASK_SECRET=clave-muy-segura-aqui

# Desarrollo
DEBUG=True
Personalización
Asignaturas: Editar la función obtener_asignaturas() en biblioteca_core.py

Estilos: Modificar static/styles.css

Plantillas: Editar archivos en templates/

🐛 Solución de Problemas
Error: "Module not found"
bash
# Asegurar que todas las dependencias estén instaladas
pip install -r requirements.txt

# O instalar manualmente:
pip install flask mysql-connector-python python-dotenv
Error de conexión a MySQL
Verificar que MySQL esté ejecutándose

Confirmar credenciales en el archivo .env

Asegurar que la base de datos biblioteca_db existe

Verificar permisos del usuario MySQL

Error: "Access denied for user"
Crear manualmente el usuario en MySQL:

sql
CREATE USER 'usuario_biblioteca'@'localhost' IDENTIFIED BY 'password123';
GRANT ALL PRIVILEGES ON biblioteca_db.* TO 'usuario_biblioteca'@'localhost';
FLUSH PRIVILEGES;
La aplicación no inicia
Verificar que estás en la carpeta proyecto_biblioteca

Confirmar que app.py existe

Revisar que Python 3.8+ esté instalado

Problemas con el archivo .env
Asegurar que el archivo se llama exactamente .env (sin .txt)

Verificar que esté en la misma carpeta que app.py

Confirmar que las variables tengan valores válidos

📝 Funcionalidades Técnicas
Autenticación segura con hash SHA-256

Relaciones muchos-a-muchos entre libros y autores

Búsquedas parciales (LIKE) en títulos y autores

Eliminación en cascada automática

Limpieza automática de autores huérfanos

Interfaz responsive para móviles y desktop

👥 Para Desarrolladores
Estructura de la Base de Datos
bibliotecarios: Usuarios del sistema

libros: Información de libros con ISBN único

prestamos: Información de préstamos activos y finalizados

autores: Autores con nombre único

libro_autor: Relación muchos-a-muchos

Extender el Sistema
Agregar nuevas tablas en scriptbiblioteca.sql

Crear nuevas rutas en app.py

Añadir funciones en biblioteca_core.py

Crear plantillas en templates/

📄 Licencia
Este proyecto fue desarrollado con fines educativos para la Tecnicatura en Programación de la Universidad de Belgrano.

🆘 Soporte
Si encuentras problemas:

Verifica que todos los pasos de instalación se siguieron correctamente

Revisa los mensajes de error en la consola

Confirma que MySQL esté funcionando

Asegúrate de que el archivo .env tenga las credenciales correctas

Comuníquese con los desarrolladores
