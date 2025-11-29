import time
import random
import math

def human_like_mouse_move(
    page,
    start,
    end,
    steps=None,          # Pasos automáticos basados en distancia
    max_deviation=10,     # Máxima desviación de la trayectoria
    delay_range=(0.005, 0.03),  # Rango de pausas entre movimientos
    curve_intensity=0.5   # Fuerza de la curvatura (0=lineal, 1=máxima curva)
):
    x0, y0 = start
    x1, y1 = end
    
    # Calcular pasos basados en distancia (más realista)
    distance = math.sqrt((x1 - x0)**2 + (y1 - y0)**2)
    if steps is None:
        steps = max(int(distance / 10), 20)  # Mínimo 20 pasos
    
    # Punto de control para curva (aleatorio)
    ctrl_x = x0 + (x1 - x0) * 0.5 + random.uniform(-max_deviation, max_deviation) * curve_intensity
    ctrl_y = y0 + (y1 - y0) * 0.5 + random.uniform(-max_deviation, max_deviation) * curve_intensity
    
    points = []
    for i in range(steps):
        t = i / max(steps - 1, 1)
        # Curva Bézier cuadrática
        x = (1 - t)**2 * x0 + 2 * (1 - t) * t * ctrl_x + t**2 * x1
        y = (1 - t)**2 * y0 + 2 * (1 - t) * t * ctrl_y + t**2 * y1
        
        # Agregar micro-desviaciones
        if 0.2 < t < 0.8:  # Solo en tramo medio
            x += random.uniform(-1.5, 1.5)
            y += random.uniform(-1.5, 1.5)
        
        points.append((x, y))
    
    # Mover con velocidad variable
    for i, point in enumerate(points):
        # Aceleración/desaceleración (más lento al inicio/final)
        speed_factor = math.sin(math.pi * i / len(points)) ** 0.8
        current_delay = random.uniform(*delay_range) * (1.5 - speed_factor)
        
        page.mouse.move(point[0], point[1])
        
        # Pausa ocasional en puntos aleatorios (simula dudas humanas)
        if i > 0 and i < len(points) - 1 and random.random() > 0.95:
            time.sleep(random.uniform(0.1, 0.3))
        else:
            time.sleep(current_delay)

def human_like_scroll(page, scroll_count=None, base_delay=(0.5, 1.2)):
    """
    Simula el scroll humano con:
    - Dirección aleatoria (arriba/abajo)
    - Velocidad variable
    - Pausas entre scrolls
    - Patrones no lineales
    """
    # Determinar cantidad de scrolls aleatorios
    if scroll_count is None:
        scroll_count = random.randint(4, 8)  # Rango más realista
    
    # Configurar dirección inicial (80% probabilidad de empezar hacia abajo)
    direction = -1 if random.random() < 0.2 else 1
    
    for i in range(scroll_count):
        # Cambiar dirección aleatoriamente (15% de probabilidad después del primer scroll)
        if i > 0 and random.random() < 0.15:
            direction *= -1  # Invertir dirección
        
        # Variación de velocidad (más rápido en medio, más lento al inicio/final)
        if i == 0 or i == scroll_count - 1:
            scroll_amount = random.randint(150, 300)  # Scrolls más cortos
        else:
            scroll_amount = random.randint(300, 600)   # Scrolls más largos
        
        # Scroll con dirección aplicada
        page.mouse.wheel(0, scroll_amount * direction)
        
        # Pausa con comportamiento humano
        if random.random() < 0.3:  # 30% probabilidad de pausa larga
            time.sleep(random.uniform(1.0, 2.5))  # Pausa de "lectura"
        else:
            time.sleep(random.uniform(*base_delay))