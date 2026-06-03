import robomaster
from robomaster import robot
import cv2
import time

if __name__ == '__main__':
    tl_drone = robot.Drone()
    tl_drone.initialize()
    
    # Get battery status
    tl_battery = tl_drone.battery
    battery_info = tl_battery.get_battery()
    print("Drone battery soc: {0}".format(battery_info))

    # Setting up camera
    tl_camera = tl_drone.camera
    tl_camera.start_video_stream(display=False)

    # --- Video Recording Setup ---
    # Usamos el codec mp4v para guardar el archivo como .mp4
    fourcc = cv2.VideoWriter_fourcc(*'mp4v')
    frame_width = 480
    frame_height = 360
    fps = 30.0 # Los drones Tello suelen transmitir a 30 fps
    
    # Crea el objeto que escribirá el video
    out = cv2.VideoWriter('fideo_circulo.mp4', fourcc, fps, (frame_width, frame_height))

    print("Grabando video... Presiona la tecla 'q' en la ventana para detener.")

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
                cv2.imshow("Recording...", frame)
                
            # Display the frame until 'q' is pressed
            if cv2.waitKey(1) & 0xFF == ord('q'):
                break

    except KeyboardInterrupt:
        print("Remote stop...")
        
    finally:
        # Cerrar y liberar todos los recursos
        print("Guardando el video y cerrando recursos...")
        out.release() # Muy importante para que el archivo de video no se corrompa
        tl_camera.stop_video_stream()
        cv2.destroyAllWindows()
        tl_drone.close()
        print("¡Video guardado como grabacion_tello.mp4!")