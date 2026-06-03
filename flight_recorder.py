import robomaster
from robomaster import robot
import cv2
import time

if __name__ == '__main__':
    tl_drone = robot.Drone()
    tl_drone.initialize()
    tl_flight = tl_drone.flight # Necesario para los comandos de vuelo
    
    # Get battery status
    tl_battery = tl_drone.battery
    battery_info = tl_battery.get_battery()
    print("Drone battery soc: {0}".format(battery_info))

    # Setting up camera
    tl_camera = tl_drone.camera
    tl_camera.start_video_stream(display=False)

    # --- Video Recording Setup ---
    fourcc = cv2.VideoWriter_fourcc(*'mp4v')
    frame_width = 480
    frame_height = 360
    fps = 30.0 
    
    # Crea el objeto que escribirá el video
    out = cv2.VideoWriter('video_circulo.mp4', fourcc, fps, (frame_width, frame_height))

    print("Despegando...")
    tl_flight.takeoff().wait_for_completed()
    time.sleep(2) # Pausa para estabilizarse en el aire

    print("Iniciando vuelo en círculo y grabando...")
    start_time = time.time()
    flight_duration = 8.0 # Duración en segundos del vuelo en círculo

    try:
        while True:
            # Read the image from the camera
            frame = tl_camera.read_cv2_image(strategy="newest", timeout=5)
            
            if frame is not None:
                # Resize to match our VideoWriter dimensions
                frame = cv2.resize(frame, (frame_width, frame_height))
                
                # Escribir el fotograma en el archivo de video
                out.write(frame)
                
                # Display the frame so you can see what is being recorded
                cv2.imshow("Recording and Flying...", frame)
                
            # --- Lógica de Vuelo (Círculo) ---
            elapsed_time = time.time() - start_time
            
            if elapsed_time < flight_duration:
                # rc(roll, pitch, throttle, yaw)
                # pitch = 30 (velocidad hacia adelante)
                # yaw = 45 (velocidad de giro en grados/seg)
                tl_flight.rc(0, 30, 0, 45)
            else:
                # Se acabó el tiempo estipulado
                print("Tiempo completado. Deteniendo rotación...")
                tl_flight.rc(0, 0, 0, 0)
                time.sleep(1) # Pausa breve para estabilizar antes de aterrizar
                break # Rompemos el ciclo while para ir al finally
                
            # Interrupción de emergencia manual
            if cv2.waitKey(1) & 0xFF == ord('q'):
                print("Aterrizaje de emergencia solicitado por teclado...")
                break

    except KeyboardInterrupt:
        print("Remote stop...")
        
    finally:
        # Cerrar y liberar todos los recursos
        print("Aterrizando...")
        tl_flight.rc(0, 0, 0, 0) # Aseguramos que los motores paren el desplazamiento
        tl_flight.land().wait_for_completed()
        
        print("Guardando el video y cerrando recursos...")
        out.release() 
        tl_camera.stop_video_stream()
        cv2.destroyAllWindows()
        tl_drone.close()
        print("¡Video guardado como video_circulo.mp4!")