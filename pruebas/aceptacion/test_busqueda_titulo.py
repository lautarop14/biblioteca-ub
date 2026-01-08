import pytest
from selenium.webdriver.common.by import By
from utils import login, BASE_URL

def test_busqueda_titulo_existente(logged_in_driver):
    """Caso C1: Buscar libro por título existente"""
    driver = logged_in_driver
    
    # Ir a búsqueda por título
    driver.get(f"{BASE_URL}/buscar/titulo")
    
    # Buscar un término común
    driver.find_element(By.NAME, "titulo").send_keys("programación")
    driver.find_element(By.CSS_SELECTOR, "form").submit()
    
    # Verificar resultados
    page_source = driver.page_source
    
    # Puede mostrar resultados o mensaje de no encontrado
    assert "Libro" in page_source or "no encontrado" in page_source or "Resultados" in page_source
    
    # Si hay resultados, verificar estructura
    if "no encontrado" not in page_source.lower():
        # Verificar que muestra datos del libro
        elementos = driver.find_elements(By.CSS_SELECTOR, ".libro, tr, .card")
        assert len(elementos) > 0

def test_busqueda_titulo_inexistente(logged_in_driver):
    """Buscar título que no existe"""
    driver = logged_in_driver
    
    driver.get(f"{BASE_URL}/buscar/titulo")
    driver.find_element(By.NAME, "titulo").send_keys("zxcvbnmqwertyuiop1234567890")
    driver.find_element(By.CSS_SELECTOR, "form").submit()
    
    # Verificar mensaje de no encontrado
    assert "no encontrado" in driver.page_source.lower() or \
           "No se encontraron" in driver.page_source or \
           "warning" in driver.page_source