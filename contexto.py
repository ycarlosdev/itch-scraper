from playwright.sync_api import sync_playwright

def crear_contexto(navegador):
    return navegador.new_context(
        user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/138.0.0.0 Safari/537.36",
        locale="es-ES",
        viewport={"width": 1280, "height": 800},
        device_scale_factor=1.0,
        is_mobile=False,
        has_touch=False,
        java_script_enabled=True,
        timezone_id="America/Toronto",
        geolocation={"longitude": -79.3832, "latitude": 43.6532},
        permissions=["geolocation"],
        extra_http_headers={
            "Accept-Language": "es-ES,es;q=0.9,en;q=0.8",
            "Referer": "https://store.steampowered.com/"
        }
    )

