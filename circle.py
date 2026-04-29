import time
from robomaster import robot 

# 1. Inicializar el dron
tl_drone = robot.Drone()
tl_drone.initialize()
tl_flight = tl_drone.flight

# 2. Despegar
print("Despegando...")
tl_flight.takeoff().wait_for_completed()

# 3. Iniciar el movimiento circular
print("Iniciando movimiento circular...")
# Mover hacia adelante (b) y girar (d) al mismo tiempo
tl_flight.rc(a=0, b=30, c=0, d=40) 

# 4. Mantener el movimiento (Ajusta los segundos según el tamaño de tu espacio)
time.sleep(8) 

# 5. Detener el movimiento
print("Deteniendo el movimiento...")
tl_flight.rc(a=0, b=0, c=0, d=0)
time.sleep(2) # Darle tiempo para estabilizarse en el aire

# 6. Aterrizar y liberar recursos
print("Aterrizando...")
tl_flight.land().wait_for_completed()

tl_drone.close()
print("¡Vuelo completado exitosamente!")