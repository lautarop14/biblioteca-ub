import pytest
import time
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import Select
from utils import login, esperar_texto, BASE_URL, buscar_libro_existente

def test_alta_libro(driver):
    """Caso L1: Alta de nuevo libro"""
    login(driver)
    
    # Ir a formulario de nuevo libro
    driver.get(f"{BASE_URL}/libros/nuevo")
    
    # Rellenar formulario
    driver.find_element(By.NAME, "titulo").send_keys("Libro de Pruebas Automatizado")
    driver.find_element(By.NAME, "autores").send_keys("Autor de Prueba 1; Autor de Prueba 2")
    driver.find_element(By.NAME, "paginas").send_keys("250")
    driver.find_element(By.NAME, "isbn").send_keys("9876543210123")
    
    # Asignatura (puede ser input text o select)
    try:
        select = Select(driver.find_element(By.NAME, "asignatura"))
        select.select_by_visible_text("Programación I")
    except:
        # Si es input text
        driver.find_element(By.NAME, "asignatura").send_keys("Programación I")
    
    # Enviar formulario
    driver.find_element(By.CSS_SELECTOR, "form").submit()
    time.sleep(1)
    
    # Verificar mensaje de éxito
    esperar_texto(driver, "Libro agregado")
    assert "Libro agregado" in driver.page_source
    
    # Verificar que aparece en listado
    driver.get(f"{BASE_URL}/libros")
    assert "Libro de Pruebas Automatizado" in driver.page_source

def test_editar_libro(logged_in_driver):
    """Caso L2: Editar libro existente"""
    driver = logged_in_driver
    
    # Buscar un libro existente
    driver.get(f"{BASE_URL}/libros")
    libros = driver.find_elements(By.TAG_NAME, "tr")
    
    if len(libros) > 1:  # Hay al menos un libro
        # Tomar el primer libro para editar
        primer_libro = libros[1]
        enlace_editar = primer_libro.find_element(By.PARTIAL_LINK_TEXT, "Editar")
        enlace_editar.click()
        
        # Modificar datos
        titulo_field = driver.find_element(By.NAME, "titulo")
        titulo_field.clear()
        titulo_field.send_keys(" [EDITADO CON SELENIUM]")
        
        autores_field = driver.find_element(By.NAME, "autores")
        autores_field.clear()
        autores_field.send_keys("Autor Modificado")
        
        # Enviar cambios
        driver.find_element(By.CSS_SELECTOR, "form").submit()
        time.sleep(1)
        
        # Verificar éxito
        esperar_texto(driver, "Libro modificado")
        assert "Libro modificado" in driver.page_source
        
        # Verificar que aparece editado en listado
        driver.get(f"{BASE_URL}/libros")
        assert "[EDITADO CON SELENIUM]" in driver.page_source
    else:
        pytest.skip("No hay libros para editar")

def test_eliminar_libro(logged_in_driver):
    """Caso L6: Eliminar libro"""
    driver = logged_in_driver
    
    # Primero crear un libro para eliminar
    driver.get(f"{BASE_URL}/libros/nuevo")
    driver.find_element(By.NAME, "titulo").send_keys("LIBRO A ELIMINAR")
    driver.find_element(By.NAME, "autores").send_keys("Autor Temporal")
    driver.find_element(By.NAME, "isbn").send_keys("9999999999999")
    driver.find_element(By.CSS_SELECTOR, "form").submit()
    time.sleep(1)
    
    # Buscar y eliminar el libro recién creado
    driver.get(f"{BASE_URL}/libros")
    
    # Encontrar todas las filas de la tabla
    filas = driver.find_elements(By.CSS_SELECTOR, "tbody tr")
    
    for fila in filas:
        if "LIBRO A ELIMINAR" in fila.text:
            # Buscar formulario de eliminar
            try:
                form = fila.find_element(By.CSS_SELECTOR, "form[action*='eliminar']")
                form.submit()
                time.sleep(1)
                
                # Manejar alerta si existe
                try:
                    alert = driver.switch_to.alert
                    alert.accept()
                    time.sleep(1)
                except:
                    pass
                
                break
            except:
                continue
    
    # Verificar eliminación
    esperar_texto(driver, "Libro eliminado")
    assert "Libro eliminado" in driver.page_source
    
    # Verificar que no aparece en listado
    driver.get(f"{BASE_URL}/libros")
    assert "LIBRO A ELIMINAR" not in driver.page_source

def test_listar_libros(logged_in_driver):
    """Caso L4: Listar todos los libros"""
    driver = logged_in_driver
    
    driver.get(f"{BASE_URL}/libros")
    
    # Verificar que carga la página
    assert "Libros" in driver.page_source
    
    # Verificar estructura de tabla
    tabla = driver.find_element(By.TAG_NAME, "table")
    assert tabla.is_displayed()
    
    # Verificar columnas esperadas
    encabezados = ["Título", "Autor", "Páginas", "ISBN", "Asignatura", "Acciones"]
    for encabezado in encabezados:
        assert encabezado in driver.page_source