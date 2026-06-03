import robomaster
from robomaster import robot
import cv2 as cv2
import numpy as np

def main():
    # Inicializar solo la conexión base con el dron
    tl_drone = robot.Drone()
    tl_drone.initialize()
    
    # Configuración de la cámara del dron
    tl_camera = tl_drone.camera
    tl_camera.start_video_stream(display=False)

    # 1. INICIALIZAR EL MÓDULO LED
    tl_led = tl_drone.led

    colores = {
        "MORADO": (np.array([125, 50, 50]), np.array([155, 255, 255]), (255, 0, 255), "FOLLOW ME", "F", "r"),
        "NARANJA": (np.array([10, 160, 160]), np.array([25, 255, 255]), (0, 165, 255), "FLIP", "V", "b"),
        "CELESTE": (np.array([85, 100, 100]), np.array([110, 255, 255]), (255, 255, 0), "HOVER", "H", "r"),
        "AMARILLO": (np.array([25, 100, 100]), np.array([35, 255, 255]), (0, 255, 255), "ATERRIZANDO", "A", "b")
    }

    MIN_AREA = 800

    print("\n" + "="*40)
    print("   PROYECTO UAV - MÁQUINA DE ESTADOS   ")
    print("="*40)
    
    # 2. VARIABLE PARA RASTREAR EL ESTADO ANTERIOR (EVITA SPAM)
    last_action = None
    
    # Limpiar la matriz al iniciar
    tl_led.set_mled_char(" ", "r")

    try:
        while True:
            frame = tl_camera.read_cv2_image(strategy="newest", timeout=5)
            
            if frame is None:
                continue
                
            frame = cv2.resize(frame, (480, 360))
            hsv = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)
            
            largest_area = 0
            best_contour = None
            draw_color = (255, 255, 255)
            action_text = "BUSCANDO"
            matrix_char = " "  # Espacio en blanco por defecto
            matrix_color = "r"

            # ESCANEAR COLORES
            for nombre, (lower, upper, color_bgr, accion, char, m_color) in colores.items():
                mask = cv2.inRange(hsv, lower, upper)
                
                kernel = np.ones((5,5), np.uint8)
                mask = cv2.morphologyEx(mask, cv2.MORPH_OPEN, kernel)
                
                contours, _ = cv2.findContours(mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
                
                if contours:
                    largest_in_mask = max(contours, key=cv2.contourArea)
                    area = cv2.contourArea(largest_in_mask)
                    
                    if area > MIN_AREA and area > largest_area:
                        largest_area = area
                        best_contour = largest_in_mask
                        draw_color = color_bgr
                        action_text = accion
                        matrix_char = char
                        matrix_color = m_color

            # 3. LÓGICA DE ACTUALIZACIÓN DE LA MATRIZ LED
            if action_text != last_action:
                print(f"Cambio de estado detectado: {action_text}")
                # Solo enviar comando si cambió el estado
                # "r" = rojo, "b" = azul
                tl_led.set_mled_char(matrix_char, matrix_color)
                last_action = action_text

            # FEEDBACK VISUAL EN PANTALLA
            if best_contour is not None:
                x, y, w, h = cv2.boundingRect(best_contour)
                cx, cy = x + w // 2, y + h // 2
                
                cv2.rectangle(frame, (x, y), (x+w, y+h), draw_color, 2)
                cv2.circle(frame, (cx, cy), 5, draw_color, -1)
                cv2.putText(frame, f"{action_text}", (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 0.8, draw_color, 2)
                cv2.putText(frame, f"Area: {int(largest_area)}", (10, 60), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 255, 255), 1)
            else:
                cv2.putText(frame, "BUSCANDO SEÑAL...", (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 255, 255), 2)
                
            cv2.imshow("Proyecto UAV - Drone Feed", frame)
            
            if cv2.waitKey(1) & 0xFF == ord('q'):
                break

    except KeyboardInterrupt:
        print("Interrupción manual...")
        
    finally:
        print("Cerrando stream de video...")
        tl_led.set_mled_char(" ", "r") # Apagar matriz al salir
        tl_camera.stop_video_stream()
        cv2.destroyAllWindows()
        tl_drone.close()

if __name__ == '__main__':
    main()