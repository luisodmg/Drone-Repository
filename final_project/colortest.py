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

    # Definir los rangos de colores en HSV para OpenCV
    # Ajuste en NARANJA: Se subió la saturación (S) y el valor (V) mínimos a 160 
    # para evitar que detecte la piel humana.
    colores = {
        "MORADO": (np.array([125, 50, 50]), np.array([155, 255, 255]), (255, 0, 255), "FIGURE 8"),
        "NARANJA": (np.array([10, 160, 160]), np.array([25, 255, 255]), (0, 165, 255), "FLIP"),
        "CELESTE": (np.array([85, 100, 100]), np.array([110, 255, 255]), (255, 255, 0), "VERTICAL SQUARE"),
        "AMARILLO": (np.array([25, 100, 100]), np.array([35, 255, 255]), (0, 255, 255), "LAND")
    }

    # Área mínima para ignorar ruido visual
    MIN_AREA = 800

    # --- Imprimir referencia en la consola ---
    print("\n" + "="*40)
    print("   PROYECTO UAV - MÁQUINA DE ESTADOS   ")
    print("="*40)
    print("Referencia de colores y acciones:")
    for color_name, (_, _, _, action) in colores.items():
        print(f" -> {color_name:<10}: {action}")
    print("="*40)
    print("Iniciando transmisión de video. Presiona 'q' en la ventana para salir.\n")

    try:
        while True:
            # Leer imagen de la cámara del dron
            frame = tl_camera.read_cv2_image(strategy="newest", timeout=5)
            
            # Evitar crasheos si el frame tarda en llegar
            if frame is None:
                continue
                
            frame = cv2.resize(frame, (480, 360))
            hsv = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)
            
            largest_area = 0
            best_contour = None
            draw_color = (255, 255, 255)
            action_text = "BUSCANDO..."

            # 1. ESCANEAR TODOS LOS COLORES
            for nombre, (lower, upper, color_bgr, accion) in colores.items():
                mask = cv2.inRange(hsv, lower, upper)
                
                # Operación morfológica para reducir ruido
                kernel = np.ones((5,5), np.uint8)
                mask = cv2.morphologyEx(mask, cv2.MORPH_OPEN, kernel)
                
                contours, _ = cv2.findContours(mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
                
                if contours:
                    largest_in_mask = max(contours, key=cv2.contourArea)
                    area = cv2.contourArea(largest_in_mask)
                    
                    # Quedarnos con el color que tenga el objeto más grande en pantalla
                    if area > MIN_AREA and area > largest_area:
                        largest_area = area
                        best_contour = largest_in_mask
                        draw_color = color_bgr
                        action_text = accion

            # 2. DIBUJAR FEEDBACK VISUAL (SIN MANDAR COMANDOS DE VUELO)
            if best_contour is not None:
                x, y, w, h = cv2.boundingRect(best_contour)
                cx, cy = x + w // 2, y + h // 2
                
                # Dibujar recuadro, centro y texto de la acción
                cv2.rectangle(frame, (x, y), (x+w, y+h), draw_color, 2)
                cv2.circle(frame, (cx, cy), 5, draw_color, -1)
                cv2.putText(frame, f"{action_text}", (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 0.8, draw_color, 2)
                
                # Imprimir el área en pantalla para ayudarte a calibrar qué tan cerca/lejos estás
                cv2.putText(frame, f"Area: {int(largest_area)}", (10, 60), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 255, 255), 1)

            else:
                # No se detectó ningún color válido
                cv2.putText(frame, "BUSCANDO SEÑAL...", (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 255, 255), 2)
                
            # Mostrar la cámara del dron en la computadora
            cv2.imshow("Proyecto UAV - Drone Feed", frame)
            if cv2.waitKey(1) & 0xFF == ord('q'):
                break

    except KeyboardInterrupt:
        print("Interrupción manual...")
        
    finally:
        # Cerrar video y conexión limpiamente
        print("Cerrando stream de video...")
        tl_camera.stop_video_stream()
        cv2.destroyAllWindows()
        tl_drone.close()

if __name__ == '__main__':
    main()