import robomaster
import time 
from robomaster import robot

if __name__ == '__main__':
    # 1. Inicializar el dron
    tl_drone = robot.Drone()
    tl_drone.initialize()

    tl_flight = tl_drone.flight
    tl_battery = tl_drone.battery

    # 2. Revisión de batería (Sección 2.1)
    battery_info = tl_battery.get_battery()
    print(f"Batería actual del dron: {battery_info}%")

    # Condición de seguridad: No despegar si la batería es menor al 10%
    if battery_info < 10:
        print("¡Batería muy baja! Abortando misión para evitar caídas.")
    else:
        print("Batería suficiente. Iniciando secuencia de vuelo...")

        # 3. Despegue
        tl_flight.takeoff().wait_for_completed()
        time.sleep(2) # Pequeña pausa para estabilizar

        # 4. Incrementar altura (Sección 2.5)
        print("Subiendo 50 cm...")
        tl_flight.up(distance=50).wait_for_completed()

        # 5. Trayectoria del Cuadrado (Sección 2.5)
        # Usaremos 100 cm (1 metro) para cada lado.
        # Nota de la práctica 2.2: Cuidado con distancias muy pequeñas (menores a 20cm), el dron puede ignorarlas.
        distancia_lado = 50
        
        print("Iniciando trayectoria de cuadrado...")
        # Lado 1: Hacia adelante
        tl_flight.forward(distance=distancia_lado).wait_for_completed()
        # Lado 2: Hacia la derecha
        tl_flight.right(distance=distancia_lado).wait_for_completed()
        # Lado 3: Hacia atrás
        tl_flight.backward(distance=distancia_lado).wait_for_completed()
        # Lado 4: Hacia la izquierda (regresa al punto de inicio)
        tl_flight.left(distance=distancia_lado).wait_for_completed()
        
        print("Cuadrado completado. Preparando descenso...")

        # 6. Bajar la altura (Sección 2.5)
        print("Bajando 50 cm...")
        tl_flight.down(distance=50).wait_for_completed()

        # 7. Aterrizar
        print("Aterrizando...")
        tl_flight.land().wait_for_completed()

    # Cerrar recursos siempre al final
    tl_drone.close()
    print("Programa terminado. ¡Éxito!")