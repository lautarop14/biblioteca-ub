from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time

BASE_URL = "http://localhost:5000"

def login(driver, usuario="admin", password="admin123"):
    """Realiza login en la aplicación"""
    driver.get(f"{BASE_URL}/login")
    
    # Limpiar campos por si hay datos previos
    driver.find_element(By.NAME, "usuario").clear()
    driver.find_element(By.NAME, "password").clear()
    
    # Ingresar credenciales
    driver.find_element(By.NAME, "usuario").send_keys(usuario)
    driver.find_element(By.NAME, "password").send_keys(password)
    driver.find_element(By.NAME, "password").submit()
    
    # Esperar a que cargue
    time.sleep(1)
    return driver

def logout(driver):
    """Realiza logout de la aplicación"""
    driver.get(f"{BASE_URL}/logout")
    time.sleep(1)
    return driver

def esperar_elemento(driver, selector, by=By.CSS_SELECTOR, timeout=10):
    """Espera a que un elemento esté presente"""
    wait = WebDriverWait(driver, timeout)
    return wait.until(EC.presence_of_element_located((by, selector)))

def esperar_texto(driver, texto, timeout=10):
    """Espera a que un texto aparezca en la página"""
    wait = WebDriverWait(driver, timeout)
    return wait.until(EC.text_to_be_present_in_element((By.TAG_NAME, "body"), texto))

def tomar_captura(driver, nombre="captura.png"):
    """Toma una captura de pantalla"""
    driver.save_screenshot(nombre)
    print(f"📸 Captura guardada: {nombre}")
    return nombre

def limpiar_campo(elemento):
    """Limpia un campo de texto"""
    elemento.clear()
    # Algunos campos necesitan enviar BACKSPACE
    elemento.send_keys("\b" * 20)

def buscar_libro_existente(driver):
    """Busca un libro existente para pruebas"""
    driver.get(f"{BASE_URL}/libros")
    libros = driver.find_elements(By.TAG_NAME, "tr")
    for libro in libros[1:]:  # Saltar encabezado
        try:
            enlace = libro.find_element(By.TAG_NAME, "a")
            return enlace.text, enlace
        except:
            continue
    return None, None