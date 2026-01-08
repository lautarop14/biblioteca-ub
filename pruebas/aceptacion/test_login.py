import pytest
from selenium.webdriver.common.by import By
from utils import BASE_URL, esperar_texto

def test_login_correcto(driver):
    """Caso A1: Login con credenciales correctas"""
    driver.get(f"{BASE_URL}/login")
    
    # Ingresar credenciales válidas
    driver.find_element(By.NAME, "usuario").send_keys("admin")
    driver.find_element(By.NAME, "password").send_keys("admin123")
    driver.find_element(By.NAME, "password").submit()
    
    # Verificar redirección a menú
    assert "/menu" in driver.current_url, "No se redirigió al menú"
    
    # Verificar mensaje de bienvenida
    esperar_texto(driver, "Bienvenido")
    assert "Bienvenido" in driver.page_source
    
    # Verificar que el usuario está en sesión
    driver.get(f"{BASE_URL}/libros")
    assert "/libros" in driver.current_url, "No se pudo acceder a libros sin login"

def test_login_incorrecto(driver):
    """Caso A2: Login con credenciales incorrectas"""
    driver.get(f"{BASE_URL}/login")
    
    # Ingresar credenciales inválidas
    driver.find_element(By.NAME, "usuario").send_keys("usuario_falso")
    driver.find_element(By.NAME, "password").send_keys("clave_falsa")
    driver.find_element(By.NAME, "password").submit()
    
    # Verificar que sigue en login
    assert "/login" in driver.current_url, "No se mantuvo en login"
    
    # Verificar mensaje de error
    esperar_texto(driver, "Usuario o contraseña inválidos")
    assert "Usuario o contraseña inválidos" in driver.page_source
    
    # Verificar que no puede acceder a menú
    driver.get(f"{BASE_URL}/menu")
    assert "/login" in driver.current_url, "Accedió sin credenciales válidas"

def test_login_campos_vacios(driver):
    """Caso adicional: Login con campos vacíos"""
    driver.get(f"{BASE_URL}/login")
    
    # Intentar login sin datos
    driver.find_element(By.NAME, "password").submit()
    
    # Verificar que sigue en login
    assert "/login" in driver.current_url
    
    # Verificar que muestra mensaje de error
    assert "Usuario o contraseña inválidos" in driver.page_source or \
           driver.find_elements(By.CLASS_NAME, "alert-danger")