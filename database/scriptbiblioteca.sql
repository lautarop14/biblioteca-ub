-- CREAR BASE DE DATOS
CREATE DATABASE IF NOT EXISTS biblioteca_db
CHARACTER SET utf8mb4
COLLATE utf8mb4_unicode_ci;

-- USAR ESA BASE DE DATOS
USE biblioteca_db;

-- CREAR USUARIO Y ASIGNAR PERMISOS
CREATE USER IF NOT EXISTS 'usuario_biblioteca'@'localhost' IDENTIFIED BY 'password123';
GRANT ALL PRIVILEGES ON biblioteca_db.* TO 'usuario_biblioteca'@'localhost';
FLUSH PRIVILEGES;

-- TABLAS DEL SISTEMA DE BIBLIOTECA

CREATE TABLE IF NOT EXISTS bibliotecarios (
    id INT AUTO_INCREMENT PRIMARY KEY,
    usuario VARCHAR(50) UNIQUE NOT NULL,
    password_hash VARCHAR(255) NOT NULL,
    nombre_completo VARCHAR(100) NOT NULL,
    fecha_creacion TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    admin BOOLEAN NOT NULL DEFAULT FALSE
);

CREATE TABLE IF NOT EXISTS libros (
    id INT AUTO_INCREMENT PRIMARY KEY,
    titulo VARCHAR(255) NOT NULL,
    paginas INT UNSIGNED,
    isbn BIGINT,
    asignatura VARCHAR(255),
    UNIQUE KEY unique_isbn (isbn),
    disponible BOOLEAN NOT NULL DEFAULT TRUE
);

CREATE TABLE IF NOT EXISTS autores (
    id INT AUTO_INCREMENT PRIMARY KEY,
    nombre VARCHAR(255) NOT NULL UNIQUE
);

CREATE TABLE IF NOT EXISTS libro_autor (
    libro_id INT,
    autor_id INT,
    PRIMARY KEY (libro_id, autor_id),
    FOREIGN KEY (libro_id) REFERENCES libros(id) ON DELETE CASCADE,
    FOREIGN KEY (autor_id) REFERENCES autores(id) ON DELETE CASCADE
);

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
    FOREIGN KEY (usuario_id) REFERENCES bibliotecarios(id)
);

INSERT INTO bibliotecarios (usuario, password_hash, nombre_completo, admin)
SELECT 'admin', SHA2('admin123', 256), 'Administrador Principal', TRUE
WHERE NOT EXISTS (SELECT 1 FROM bibliotecarios WHERE usuario = 'admin');

INSERT INTO bibliotecarios (usuario, password_hash, nombre_completo)
SELECT 'lautarop', SHA2('laupaz14', 256), 'Lautaro Paz'
WHERE NOT EXISTS (SELECT 1 FROM bibliotecarios WHERE usuario = 'lautarop');
