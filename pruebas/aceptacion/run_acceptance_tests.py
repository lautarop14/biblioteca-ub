#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Runner mejorado para pruebas de aceptación:
- Inicia la app Flask con subprocess.Popen (control del proceso)
- Espera activamente la disponibilidad via HTTP (health-check)
- Ejecuta pytest y genera report.html
- Cierra el proceso Flask al finalizar
"""

import subprocess
import sys
import os
import time
import webbrowser
import requests
from threading import Thread

# Ajusta estas constantes si es necesario
APP_PY_PATH = os.path.join("..", "app.py")
APP_URL = "http://127.0.0.1:5000"
HEALTH_ENDPOINT = "/health"  # si no existe, el runner probara "/"
START_TIMEOUT = 20  # segundos para esperar que la app levante

def iniciar_aplicacion():
    """
    Inicia la aplicación Flask en segundo plano y retorna el Popen object.
    """
    print("[+] Iniciando aplicación Flask (subprocess)...")
    env = os.environ.copy()
    # Desactivar reloader (evita procesos hijos)
    env['FLASK_DEBUG'] = '0'
    # Ejecutamos el app.py con python3 (ajustar ruta si es necesario)
    p = subprocess.Popen([sys.executable, APP_PY_PATH], env=env, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
    return p

def esperar_app_lista(url_base=APP_URL, endpoint=HEALTH_ENDPOINT, timeout=START_TIMEOUT):
    """
    Intenta hacer GET al endpoint hasta que responda HTTP 200 o se agote timeout.
    Si no existe /health, intenta con '/'.
    Retorna True si la app respondió, False si timeout.
    """
    start = time.time()
    endpoint_to_try = endpoint
    while time.time() - start < timeout:
        try:
            r = requests.get(url_base + endpoint_to_try, timeout=1)
            if r.status_code == 200:
                print("[+] Aplicación lista (health ok).")
                return True
        except Exception:
            # si probamos /health y no existe, probar con '/'
            if endpoint_to_try != "/":
                endpoint_to_try = "/"
            time.sleep(0.5)
    print("[-] Timeout esperando que la app responda.")
    return False

def ejecutar_pruebas():
    """Ejecuta pytest con las opciones definidas y devuelve el código de salida."""
    print("\n" + "="*60)
    print("EJECUTANDO PRUEBAS DE ACEPTACIÓN")
    print("="*60)

    cmd = [
        sys.executable, "-m", "pytest",
        "-v",
        "--tb=short",
        "--html=report.html",
        "--self-contained-html",
        "--capture=no",
    ]
    print(f"\nComando: {' '.join(cmd)}")

    # Ejecutar pytest y capturar salida
    result = subprocess.run(cmd, capture_output=True, text=True)
    print("\nRESULTADOS:")
    print("="*60)
    print(result.stdout)
    if result.stderr:
        print("\nERRORES:")
        print(result.stderr)

    exit_code = result.returncode
    if exit_code == 0:
        print("\n[+] ¡Todas las pruebas pasaron!")
    else:
        print(f"\n[-] Algunas pruebas fallaron (código: {exit_code})")

    generar_reporte_simple()
    return exit_code

def generar_reporte_simple():
    reporte = """
    ========================================
    REPORTE DE PRUEBAS DE ACEPTACIÓN
    ========================================

    Revisa report.html para el detalle. resultado_pruebas.txt es un resumen.

    ========================================
    INSTRUCCIONES:
    - Reporte HTML: report.html
    - Capturas de error: carpeta screenshots/
    - Ejecutar prueba individual: pytest nombre_prueba.py -v
    ========================================
    """
    with open("resultado_pruebas.txt", "w", encoding="utf-8") as f:
        f.write(reporte)
    print("\n[*] Reporte generado: resultado_pruebas.txt")
    print("[*] Reporte HTML: report.html")

def main():
    print("="*60)
    print("SISTEMA DE PRUEBAS DE ACEPTACIÓN - BIBLIOTECA")
    print("="*60)

    if not os.path.exists("conftest.py"):
        print("[-] Error: Debes ejecutar desde la carpeta pruebas_aceptacion/")
        print("   cd pruebas_aceptacion")
        print("   python run_acceptance_tests.py")
        return 1

    flask_proc = None
    try:
        # Iniciar app
        flask_proc = iniciar_aplicacion()

        # Esperar que la app esté lista mediante health-check
        ready = esperar_app_lista()
        if not ready:
            # Si no responde, leer stderr/stdout del proceso para debugging
            try:
                out, err = flask_proc.communicate(timeout=1)
                print("[DEBUG] stdout:\n", out)
                print("[DEBUG] stderr:\n", err)
            except Exception:
                pass
            print("[-] No fue posible verificar que la app esté lista. Abortando pruebas.")
            return 2

        # Ejecutar pytest
        exit_code = ejecutar_pruebas()

        # Preguntar si abrir reporte
        if os.path.exists("report.html"):
            abrir = input("\nAbrir reporte HTML en navegador? (s/n): ").lower()
            if abrir == 's':
                webbrowser.open("file://" + os.path.abspath("report.html"))

        return exit_code

    except KeyboardInterrupt:
        print("\n\n[-] Pruebas interrumpidas por el usuario")
        return 130
    finally:
        # Asegurarse de terminar proceso Flask si está en ejecución
        if flask_proc:
            print("[*] Terminando proceso de la aplicación Flask...")
            try:
                flask_proc.terminate()
                try:
                    flask_proc.wait(timeout=5)
                except Exception:
                    flask_proc.kill()
            except Exception as e:
                print(f"[WARN] No se pudo terminar proceso Flask: {e}")
        print("\n" + "="*60)
        print("FIN DE EJECUCIÓN")
        print("="*60)

if __name__ == "__main__":
    sys.exit(main())