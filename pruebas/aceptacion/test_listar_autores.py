import pytest
from selenium.webdriver.common.by import By
from utils import login, BASE_URL

def test_listar_autores(logged_in_driver):
    """Caso AU1: Listar autores"""
    driver = logged_in_driver
    
    driver.get(f"{BASE_URL}/autores")
    
    # Verificar título
    assert "Autores" in driver.page_source
    
    # Verificar que muestra la lista
    lista = driver.find_elements(By.TAG_NAME, "li")
    assert len(lista) > 0 or "No hay autores" in driver.page_source
    
    # Verificar funcionalidad de limpiar autores huérfanos si existe
    if "Limpiar autores huérfanos" in driver.page_source:
        enlace = driver.find_element(By.PARTIAL_LINK_TEXT, "huérfanos")
        enlace.click()
        assert "eliminados" in driver.page_source or "Autores" in driver.page_source

def test_autores_se_crean_con_libro(logged_in_driver):
    """Verificar que al crear libro se crean autores"""
    driver = logged_in_driver
    
    # Crear libro con autores nuevos
    driver.get(f"{BASE_URL}/libros/nuevo")
    driver.find_element(By.NAME, "titulo").send_keys("Libro con Autores Nuevos")
    driver.find_element(By.NAME, "autores").send_keys("Autor Selenium Uno; Autor Selenium Dos")
    driver.find_element(By.NAME, "isbn").send_keys("1112223334445")
    driver.find_element(By.CSS_SELECTOR, "form").submit()
    
    # Verificar que los autores aparecen en la lista
    driver.get(f"{BASE_URL}/autores")
    
    # Tomar captura para debug
    driver.save_screenshot("autores_despues_creacion.png")
    
    assert "Autor Selenium Uno" in driver.page_source
    assert "Autor Selenium Dos" in driver.page_source