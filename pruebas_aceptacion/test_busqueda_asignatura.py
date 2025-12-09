import pytest
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import Select
from utils import login, BASE_URL

def test_busqueda_asignatura(logged_in_driver):
    """Caso C5: Buscar libros por asignatura"""
    driver = logged_in_driver
    
    # Crear libro con asignatura específica
    driver.get(f"{BASE_URL}/libros/nuevo")
    driver.find_element(By.NAME, "titulo").send_keys("Libro Asignatura Especial")
    driver.find_element(By.NAME, "autores").send_keys("Autor Prueba")
 
    select_asignatura = Select(driver.find_element(By.NAME, "asignatura"))
    select_asignatura.select_by_visible_text("Sistemas Operativos") 
    
    driver.find_element(By.NAME, "isbn").send_keys("1313131313131")
    driver.find_element(By.CSS_SELECTOR, "form").submit()
    
    # Buscar por esa asignatura
    driver.get(f"{BASE_URL}/buscar/asignatura")
    
    select_busqueda = Select(driver.find_element(By.NAME, "asignatura"))
    select_busqueda.select_by_visible_text("Sistemas Operativos")
    
    driver.find_element(By.CSS_SELECTOR, "form").submit()
    
    # Verificar resultados
    assert "Libro Asignatura Especial" in driver.page_source
    assert "ASIGNATURA_ESPECIAL_SELENIUM" in driver.page_source
    
    # Buscar asignatura sin seleccionar - Caso C6 
    driver.get(f"{BASE_URL}/buscar/asignatura")
    
    driver.find_element(By.CSS_SELECTOR, "form").submit()
    
    # Verificar mensaje apropiado de "no encontrado"
    assert any(text in driver.page_source.lower() for text in ["no se encontraron", "warning", "no encontrado"])
