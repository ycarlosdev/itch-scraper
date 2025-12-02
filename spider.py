import logging
import time
from itertools import zip_longest
import pandas as pd
from playwright.sync_api import sync_playwright
from utils.contexto import crear_contexto
from utils.simulacion import human_like_mouse_move, human_like_scroll
from utils.detectar_plataforma import reconocer_plataforma
from selectolax.lexbor import LexborHTMLParser


logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s"
)

# ENTRADA: Clase encargada de abrir la página
class Entrada:
    def __init__(self, url):
        self.url = url
        self.browser = None
        self.page = None

    def abrir(self):
        """Abre el navegador, la página y ejecuta el scroll inicial."""
        logging.info("Iniciando Playwright...")

        playwright = sync_playwright().start()
        self.browser = playwright.chromium.launch(headless=True)

        logging.info("Creando contexto personalizado...")
        contexto = crear_contexto(self.browser)

        self.page = contexto.new_page()
        logging.info(f"Accediendo a {self.url}")
        self.page.goto(self.url, timeout=120000)

        time.sleep(3)

        # Movimiento inicial humano
        human_like_mouse_move(
            self.page,
            start=(200, 150),
            end=(500, 800),
            steps=60,
            max_deviation=12,
            delay_range=(0.01, 0.04),
            curve_intensity=0.7
        )
        return self.page

    def scroll_progresivo(self, veces=5):
        """Scroll humano progresivo para cargar más juegos."""
        logging.info(f"Realizando scroll progresivo {veces} veces...")
        human_like_scroll(self.page, scroll_count=veces, base_delay=(0.6, 1.3))

    def obtener_html(self):
        return self.page.content()

    def cerrar(self):
        if self.browser:
            self.browser.close()


# SCRAPER: Clase que extrae datos del HTML
class Scraper:
    def __init__(self, html):
        self.parser = LexborHTMLParser(html)

    def obtener_datos(self):
        """Extrae todos los datos visibles actualmente."""
        nombres = [
            n.text(strip=True)
            for n in self.parser.css("div.game_title a")
        ]

        provedores = [
            n.text(strip=True)
            for n in self.parser.css("div.game_author a")
        ]

        descripciones = [
            n.text(strip=True)
            for n in self.parser.css("div.game_text")
        ]

        generos = [
            n.text(strip=True)
            for n in self.parser.css("div.game_genre")
        ]
        
        enlaces_provedor = [
            n.attributes.get('href')
            for n in self.parser.css("div.game_author a")
        ]
        
        urls_img = [
            n.attributes.get('src')
            for n in self.parser.css("img.lazy_loaded")
        ]
        
        plataforma = [
            n for n in self.parser.css("div.game_platform")
        ]
        
        # Detectando de qué plataforma son los videojuegos
        lista_plataformas = []

        for div in plataforma:  # 'div' es cada elemento div.plataforma
            # Para cada div, obtenemos TODOS sus spans con title
            spans_del_div = div.css("span")
            
            plataformas_del_div = []  # Lista para las plataformas de ESTE div específico
            
            for span in spans_del_div:
                # Accedemos al atributo title del span, no del div
                titulo = span.attributes.get('title')
                
                if titulo:  # Verificamos que el título no sea None
                    plataforma_detectada = reconocer_plataforma(titulo)
                    if plataforma_detectada is not None:
                        plataformas_del_div.extend(plataforma_detectada)
            
            # Agregamos la lista de plataformas de este div a la lista principal
            lista_plataformas.append(plataformas_del_div)

        return [nombres, provedores, descripciones, generos, enlaces_provedor, urls_img, lista_plataformas]


# GUARDAR DATOS: Clase para acumular y guardar
class GuardarDatos:
    def __init__(self):
        self.nombre = []
        self.provedor = []
        self.descripcion = []
        self.genero = []
        self.enlace_provedor = []
        self.url_img = []
        self.plataforma = []

    def acumular(self, lista_datos):
        nombres, provedores, descripciones, generos, enlaces_provedor, urls_img, lista_plataformas = lista_datos

        for n, p, d, g, e, u, l in zip_longest(nombres, provedores, descripciones, generos, enlaces_provedor, urls_img, lista_plataformas):
            self.nombre.append(n)
            self.provedor.append(p)
            self.descripcion.append(d)
            self.genero.append(g)
            self.enlace_provedor.append(e)
            self.url_img.append(u)
            self.plataforma.append(l)

    def cantidad(self):
        return len(self.nombre)

    def guardar_csv(self):
        df = pd.DataFrame({
            "nombre": self.nombre,
            "provedor": self.provedor,
            "descripcion": self.descripcion,
            "genero": self.genero,
            "enlace_provedor": self.enlace_provedor,
            "url_imagen": self.url_img,
            "plataforma": self.plataforma
        })
        df.to_csv("datos-videojuegos.csv", index=False)
        logging.info("CSV generado correctamente.")


# LOOP PRINCIPAL DEL SCRAPER
if __name__ == "__main__":
    URL = "https://itch.io/games"
    MAX_DATOS = 1000

    extractor_total = GuardarDatos()
    navegador = Entrada(URL)

    try:
        pagina = navegador.abrir()

        while extractor_total.cantidad() < MAX_DATOS:

            # Scroll → cargar más datos
            navegador.scroll_progresivo(veces=4)

            # Extraer HTML actualizado
            html = navegador.obtener_html()

            scraper = Scraper(html)
            datos = scraper.obtener_datos()

            # Acumular datos
            extractor_total.acumular(datos)

            logging.info(f"Acumulados: {extractor_total.cantidad()} / {MAX_DATOS}")

        extractor_total.guardar_csv()

    finally:
        navegador.cerrar()
