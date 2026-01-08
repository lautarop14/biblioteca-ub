import pytest
import sys
import os
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from webdriver_manager.chrome import ChromeDriverManager
import time

# Configuración global
BASE_URL = "http://localhost:5000"

@pytest.fixture(scope="session")
def driver():
    """Fixture que proporciona el driver de Chrome para todas las pruebas"""
    options = Options()
    options.add_argument("--start-maximized")
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")
    options.add_argument("--disable-gpu")
    options.add_argument("--headless")  # Descomentar para ejecución sin interfaz
    
    service = Service(ChromeDriverManager().install())
    driver = webdriver.Chrome(service=service, options=options)
    driver.implicitly_wait(5)
    
    yield driver
    
    # Teardown
    driver.quit()

@pytest.fixture
def logged_in_driver(driver):
    """Fixture que proporciona un driver ya logueado"""
    from utils import login
    login(driver)
    yield driver
    # No cerramos el driver aquí, lo hace el fixture principal

def pytest_exception_interact(node, call, report):
    """Toma captura de pantalla cuando una prueba falla"""
    if report.failed and "driver" in node.fixturenames:
        driver = node.funcargs["driver"]
        timestamp = time.strftime("%Y%m%d_%H%M%S")
        screenshot_name = f"screenshots/fail_{node.name}_{timestamp}.png"
        
        # Crear directorio si no existe
        os.makedirs("screenshots", exist_ok=True)
        
        try:
            driver.save_screenshot(screenshot_name)
            print(f"\n📸 Captura de pantalla guardada: {screenshot_name}")
        except:
            pass