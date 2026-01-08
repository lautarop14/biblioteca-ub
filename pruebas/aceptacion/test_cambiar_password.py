import pytest
from selenium.webdriver.common.by import By
from utils import login, esperar_texto

def test_cambiar_password(driver):
    """Caso A4: Cambiar contraseña y restaurar"""
    # Login con contraseña original
    login(driver, "admin", "admin123")
    
    # Ir a cambiar contraseña
    driver.get("http://localhost:5000/cambiar_password")
    
    # Cambiar contraseña
    driver.find_element(By.NAME, "password_actual").send_keys("admin123")
    driver.find_element(By.NAME, "nueva_password").send_keys("nueva123")
    driver.find_element(By.NAME, "confirmar_password").send_keys("nueva123")
    driver.find_element(By.NAME, "confirmar_password").submit()
    
    # Verificar que cerró sesión
    assert "/login" in driver.current_url, "No cerró sesión después de cambiar contraseña"
    
    # Login con nueva contraseña
    driver.find_element(By.NAME, "usuario").send_keys("admin")
    driver.find_element(By.NAME, "password").send_keys("nueva123")
    driver.find_element(By.NAME, "password").submit()
    
    # Verificar login exitoso
    assert "/menu" in driver.current_url, "No pudo login con nueva contraseña"
    
    # Restaurar contraseña original
    driver.get("http://localhost:5000/cambiar_password")
    driver.find_element(By.NAME, "password_actual").send_keys("nueva123")
    driver.find_element(By.NAME, "nueva_password").send_keys("admin123")
    driver.find_element(By.NAME, "confirmar_password").send_keys("admin123")
    driver.find_element(By.NAME, "confirmar_password").submit()
    
    # Verificar que se restauró
    assert "/login" in driver.current_url, "No cerró sesión al restaurar contraseña"
    
    # Verificar que funciona con contraseña original
    driver.find_element(By.NAME, "usuario").send_keys("admin")
    driver.find_element(By.NAME, "password").send_keys("admin123")
    driver.find_element(By.NAME, "password").submit()
    
    assert "/menu" in driver.current_url, "No funciona con contraseña restaurada"

def test_cambiar_password_errores(driver):
    """Casos de error en cambio de contraseña"""
    login(driver)
    driver.get("http://localhost:5000/cambiar_password")
    
    # Contraseñas no coinciden
    driver.find_element(By.NAME, "password_actual").send_keys("admin123")
    driver.find_element(By.NAME, "nueva_password").send_keys("nueva123")
    driver.find_element(By.NAME, "confirmar_password").send_keys("diferente")
    driver.find_element(By.NAME, "confirmar_password").submit()
    
    assert "Las contraseñas no coinciden" in driver.page_source
    
    # Contraseña actual incorrecta
    driver.find_element(By.NAME, "password_actual").clear()
    driver.find_element(By.NAME, "nueva_password").clear()
    driver.find_element(By.NAME, "confirmar_password").clear()
    
    driver.find_element(By.NAME, "password_actual").send_keys("incorrecta")
    driver.find_element(By.NAME, "nueva_password").send_keys("nueva123")
    driver.find_element(By.NAME, "confirmar_password").send_keys("nueva123")
    driver.find_element(By.NAME, "confirmar_password").submit()
    
    assert "Contraseña actual incorrecta" in driver.page_source or \
           "Usuario no encontrado" in driver.page_source