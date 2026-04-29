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

    # Condición de seguridad
    if battery_info < 10:
        print("¡Batería muy baja! Abortando misión para evitar caídas.")
    else:
        print("Batería suficiente. Iniciando secuencia de vuelo...")

        # 3. Despegue
        tl_flight.takeoff().wait_for_completed()
        time.sleep(2) # Pequeña pausa para estabilizar

        # 4. Incrementar altura
        print("Subiendo 50 cm...")
        tl_flight.up(distance=50).wait_for_completed()

        # 5. Trayectoria del Triángulo Equilátero
        distancia_lado = 100 # Subí a 100cm para que la figura se trace súper clara
        angulo_giro = 120    # 120 grados para cerrar el triángulo
        
        print("Iniciando trayectoria de triángulo...")
        
        # Usamos un ciclo de 3 pasos para los 3 lados
        for i in range(3):
            print(f"Trazando lado {i+1}...")
            # Avanzar
            tl_flight.forward(distance=distancia_lado).wait_for_completed()
            
            # Girar (excepto en el último lado porque ya regresó al inicio)
            if i < 2:
                print("Girando 120 grados...")
                tl_flight.rotate(angle=angulo_giro).wait_for_completed()
        
        print("Triángulo completado. Preparando descenso...")

        # 6. Bajar la altura
        print("Bajando 50 cm...")
        tl_flight.down(distance=50).wait_for_completed()

        # 7. Aterrizar
        print("Aterrizando...")
        tl_flight.land().wait_for_completed()

    # Cerrar recursos siempre al final
    tl_drone.close()
    print("Programa terminado. ¡Éxito!")