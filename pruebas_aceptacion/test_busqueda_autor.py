import pytest
from selenium.webdriver.common.by import By
from utils import login, BASE_URL

def test_busqueda_autor(logged_in_driver):
    """Caso C3: Buscar libros por autor"""
    driver = logged_in_driver
    
    # Primero crear un libro con autor específico
    driver.get(f"{BASE_URL}/libros/nuevo")
    driver.find_element(By.NAME, "titulo").send_keys("Libro para Buscar por Autor")
    driver.find_element(By.NAME, "autores").send_keys("Autor Especial Para Buscar")
    driver.find_element(By.NAME, "isbn").send_keys("1212121212121")
    driver.find_element(By.CSS_SELECTOR, "form").submit()
    
    # Ahora buscar por ese autor
    driver.get(f"{BASE_URL}/buscar/autor")
    driver.find_element(By.NAME, "autor").send_keys("Autor Especial Para Buscar")
    driver.find_element(By.CSS_SELECTOR, "form").submit()
    
    # Verificar resultados
    assert "Libro para Buscar por Autor" in driver.page_source
    
    # Verificar que el autor aparece en resultados
    assert "Autor Especial Para Buscar" in driver.page_source
    
    # Buscar autor que no existe
    driver.get(f"{BASE_URL}/buscar/autor")
    driver.find_element(By.NAME, "autor").send_keys("AutorInexistenteXYZ123")
    driver.find_element(By.CSS_SELECTOR, "form").submit()
    
    # Verificar mensaje apropiado
    assert "No se encontraron" in driver.page_source or \
           "warning" in driver.page_source or \
           "no encontrado" in driver.page_source.lower()