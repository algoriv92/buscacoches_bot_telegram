from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
import time
import requests
from bs4 import BeautifulSoup
import re
import os

# CONFIGURACIÓN TELEGRAM
TELEGRAM_TOKEN = "8108934435:AAE8QK8Z8BEdrKyUyZnU6mSyViee2ZKc8tM"
TELEGRAM_CHAT_ID = "547542061"

# CONFIGURACIÓN SELENIUM
CHROMEDRIVER_PATH = "chromedriver.exe"  # o la ruta completa si está fuera del script

# ARCHIVO PARA GUARDAR ENLACES ENVIADOS
ENVIADOS_PATH = "enlaces_enviados.txt"

def cargar_enlaces_enviados():
    if os.path.exists(ENVIADOS_PATH):
        with open(ENVIADOS_PATH, "r", encoding="utf-8") as f:
            return set(line.strip() for line in f)
    return set()

def guardar_enlaces_enviados(enlaces):
    with open(ENVIADOS_PATH, "a", encoding="utf-8") as f:
        for enlace in enlaces:
            f.write(enlace + "\n")

# FUNCIONES PRINCIPALES

def buscar_autocasion():
    resultados = []
    headers = {"User-Agent": "Mozilla/5.0"}
    pagina = 1
    MAX_PAGINAS = 50

    os.makedirs("debug_basura", exist_ok=True)
    enviados = cargar_enlaces_enviados()

    while pagina <= MAX_PAGINAS:
        url = f"https://www.autocasion.com/coches-segunda-mano/madrid/diesel/cambio-automatic/precio-hasta-10000/km-hasta-140000?orderBy=precio-asc={pagina}"
        resp = requests.get(url, headers=headers)
        soup = BeautifulSoup(resp.text, 'html.parser')

        with open(f"debug_basura/autocasion_p{pagina}.html", "w", encoding="utf-8") as f:
            f.write(soup.prettify())

        articulos = soup.select("article")
        if not articulos:
            break

        for article in articulos:
            enlace_tag = article.select_one("a[href^='/coches-segunda-mano/']")
            if enlace_tag:
                href = f"https://www.autocasion.com{enlace_tag.get('href')}"
                if href in enviados:
                    continue
                resultados.append(href)

        pagina += 1
        time.sleep(1)  # para evitar ser bloqueado

    print(f"[Autocasión] Encontrados {len(resultados)} anuncios nuevos bajo 10.000 €")
    return resultados

def enviar_telegram(anuncios):
    print("Enviando anuncios por Telegram...")
    if not anuncios:
        print("No hay anuncios nuevos para enviar.")
        return

    for anuncio in anuncios:
        mensaje = f"🚗 Nuevo coche encontrado:\n{anuncio}"
        url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage"
        data = {"chat_id": TELEGRAM_CHAT_ID, "text": mensaje}
        requests.post(url, data=data)

    guardar_enlaces_enviados(anuncios)

# FLUJO PRINCIPAL
if __name__ == "__main__":
    anuncios_encontrados = buscar_autocasion()
    enviar_telegram(anuncios_encontrados)
