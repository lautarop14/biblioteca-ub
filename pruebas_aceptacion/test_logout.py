import pytest
from selenium.webdriver.common.by import By
from utils import login, logout, esperar_texto, BASE_URL

def test_logout(driver):
    """Caso A3: Cerrar sesión correctamente"""
    # Primero login
    login(driver)
    
    # Verificar que está logueado
    driver.get(f"{BASE_URL}/libros")
    assert "/libros" in driver.current_url, "No se pudo acceder estando logueado"
    
    # Hacer logout
    logout(driver)
    
    # Verificar que redirige a login
    assert "/login" in driver.current_url, "No redirigió a login después de logout"
    
    # Verificar mensaje de sesión cerrada
    esperar_texto(driver, "Sesión cerrada")
    assert "Sesión cerrada" in driver.page_source
    
    # Verificar que no puede acceder a páginas protegidas
    driver.get(f"{BASE_URL}/menu")
    assert "/login" in driver.current_url, "Pudo acceder después de logout"
    
    driver.get(f"{BASE_URL}/libros")
    assert "/login" in driver.current_url, "Pudo acceder después de logout"