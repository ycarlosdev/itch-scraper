import re

def reconocer_plataforma(texto):
    texto_modificado = texto.lower()
    plataforma = re.findall(r"windows|macos|android|linux|ios",texto_modificado)
    return plataforma

