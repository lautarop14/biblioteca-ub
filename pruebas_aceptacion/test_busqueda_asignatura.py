import pytest
from selenium.webdriver.common.by import By
from utils import login, BASE_URL

def test_busqueda_asignatura(logged_in_driver):
    """Caso C5: Buscar libros por asignatura"""
    driver = logged_in_driver
    
    # Crear libro con asignatura específica
    driver.get(f"{BASE_URL}/libros/nuevo")
    driver.find_element(By.NAME, "titulo").send_keys("Libro Asignatura Especial")
    driver.find_element(By.NAME, "autores").send_keys("Autor Prueba")
    
    # Asignatura especial para búsqueda
    asignatura_input = driver.find_element(By.NAME, "asignatura")
    asignatura_input.clear()
    asignatura_input.send_keys("ASIGNATURA_ESPECIAL_SELENIUM")
    
    driver.find_element(By.NAME, "isbn").send_keys("1313131313131")
    driver.find_element(By.CSS_SELECTOR, "form").submit()
    
    # Buscar por esa asignatura
    driver.get(f"{BASE_URL}/buscar/asignatura")
    driver.find_element(By.NAME, "asignatura").send_keys("ASIGNATURA_ESPECIAL_SELENIUM")
    driver.find_element(By.CSS_SELECTOR, "form").submit()
    
    # Verificar resultados
    assert "Libro Asignatura Especial" in driver.page_source
    assert "ASIGNATURA_ESPECIAL_SELENIUM" in driver.page_source
    
    # Buscar asignatura que no existe
    driver.get(f"{BASE_URL}/buscar/asignatura")
    driver.find_element(By.NAME, "asignatura").send_keys("ASIGNATURA_INEXISTENTE_XYZ")
    driver.find_element(By.CSS_SELECTOR, "form").submit()
    
    # Verificar mensaje apropiado
    assert "No se encontraron" in driver.page_source or \
           "warning" in driver.page_source or \
           "no encontrado" in driver.page_source.lower()

def test_busqueda_asignatura_comun(logged_in_driver):
    """Buscar por asignatura común como Programación"""
    driver = logged_in_driver
    
    driver.get(f"{BASE_URL}/buscar/asignatura")
    driver.find_element(By.NAME, "asignatura").send_keys("Programación")
    driver.find_element(By.CSS_SELECTOR, "form").submit()
    
    # Verificar que muestra resultados o mensaje apropiado
    page_text = driver.page_source.lower()
    assert "libro" in page_text or "no se encontraron" in page_text or "resultados" in page_text