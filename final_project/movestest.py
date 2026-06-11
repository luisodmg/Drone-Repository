import robomaster
from robomaster import robot
import cv2 as cv2
import numpy as np
import time
import threading
import sys  # Importado para asegurar el cierre total del programa

# Variable global para manejar el estado del dron sin bloquear el video
estado_dron = {
    "modo": "HOVERING",  
    "ultimo_visto": time.time()
}

# ==========================================
# DEFINICIÓN DE MANIOBRAS (HILOS SEPARADOS)
# ==========================================

def ejecutar_cuadrado(tl_drone):
    print("\n[MANIOBRA] Iniciando CUADRADO VERTICAL...")
    dist = 40 
    tl_drone.flight.up(distance=dist).wait_for_completed()
    tl_drone.flight.right(distance=dist).wait_for_completed()
    tl_drone.flight.down(distance=dist).wait_for_completed()
    tl_drone.flight.left(distance=dist).wait_for_completed()
    print("[MANIOBRA] Cuadrado terminado. Volviendo a escanear...")
    estado_dron["ultimo_visto"] = time.time()
    estado_dron["modo"] = "HOVERING"

def ejecutar_tornado(tl_drone):
    print("\n[MANIOBRA] Iniciando TORNADO (Ascenso giratorio)...")
    
    # 1. Ganar altura inicial por seguridad para no rozar el piso
    print("   -> Ganando altura de seguridad (40 cm)...")
    tl_drone.flight.up(distance=40).wait_for_completed()
    
    # 2. Ascender girando (Más tiempo y más giro)
    print("   -> Subiendo en espiral...")
    tl_drone.flight.rc(a=0, b=0, c=35, d=100) 
    time.sleep(3.5)
    
    # 3. Pausa breve en la cima
    tl_drone.flight.rc(a=0, b=0, c=0, d=0)
    time.sleep(0.5)
    
    # 4. Descender girando en sentido contrario
    print("   -> Bajando en espiral...")
    tl_drone.flight.rc(a=0, b=0, c=-35, d=-100)
    time.sleep(3.5)
    
    # 5. Detener motores para estabilizar
    tl_drone.flight.rc(a=0, b=0, c=0, d=0)
    time.sleep(1)
    
    # 6. Bajar los 40 cm iniciales
    print("   -> Regresando a la altitud inicial...")
    tl_drone.flight.down(distance=40).wait_for_completed()
    
    print("[MANIOBRA] Tornado terminado. Volviendo a escanear...")
    estado_dron["ultimo_visto"] = time.time()
    estado_dron["modo"] = "HOVERING"

def ejecutar_circulo(tl_drone):
    print("\n[MANIOBRA] Iniciando CÍRCULO...")
    time.sleep(1)
    
    print("   -> Ejecutando círculo...")
    for _ in range(2):
        tl_drone.flight.rc(a=0, b=30, c=0, d=40)
        time.sleep(8)

    tl_drone.flight.rc(a=0, b=0, c=0, d=0)
    time.sleep(2)
    print("[MANIOBRA] Círculo terminado. Volviendo a escanear...")
    
    estado_dron["ultimo_visto"] = time.time()
    estado_dron["modo"] = "HOVERING"

# ==========================================
# FUNCIÓN PRINCIPAL
# ==========================================

def main():
    tl_drone = robot.Drone()
    tl_drone.initialize()
    
    tl_camera = tl_drone.camera
    tl_camera.start_video_stream(display=False)

    colores = {
        "MORADO": (np.array([125, 50, 50]), np.array([155, 255, 255]), (255, 0, 255), "CIRCLE"),
        "NARANJA": (np.array([5, 80, 80]), np.array([30, 255, 255]), (0, 165, 255), "TORNADO"),
        "CELESTE": (np.array([85, 100, 100]), np.array([110, 255, 255]), (255, 255, 0), "VERTICAL SQUARE"),
        "VERDE": (np.array([40, 50, 50]), np.array([80, 255, 255]), (0, 255, 0), "LAND")
    }

    MIN_AREA = 800
    
    # Variables de Control y Tracking
    FRAMES_REQUERIDOS = 10
    conteo_frames = 0
    accion_en_mira = None
    accion_pendiente = None
    inicio_tracking = 0
    
    # Centro de la imagen (Resolución 480x360)
    CENTER_X, CENTER_Y = 240, 180

    print("\n" + "="*40)
    print("   PROYECTO UAV - MÁQUINA DE ESTADOS   ")
    print("="*40)
    
    print("\n[VUELO] Despegando...")
    tl_drone.flight.takeoff().wait_for_completed()
    print("[VUELO] Dron en el aire. Esperando 5 segundos para estabilizar cámara...")
    time.sleep(5)
    estado_dron["ultimo_visto"] = time.time()

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
            action_text = "BUSCANDO..."

            # Solo escaneamos colores si estamos flotando o en pleno tracking
            if estado_dron["modo"] in ["HOVERING", "TRACKING"]:
                for nombre, (lower, upper, color_bgr, accion) in colores.items():
                    mask = cv2.inRange(hsv, lower, upper)
                    kernel = np.ones((5,5), np.uint8)
                    mask = cv2.morphologyEx(mask, cv2.MORPH_OPEN, kernel)
                    
                    contours, _ = cv2.findContours(mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
                    
                    if contours:
                        largest_in_mask = max(contours, key=cv2.contourArea)
                        area = cv2.contourArea(largest_in_mask)
                        
                        if area > MIN_AREA and area > largest_area:
                            # Si estamos en tracking, ignoramos otros colores que no sean nuestro objetivo
                            if estado_dron["modo"] == "HOVERING" or (estado_dron["modo"] == "TRACKING" and accion == accion_pendiente):
                                largest_area = area
                                best_contour = largest_in_mask
                                draw_color = color_bgr
                                action_text = accion

            # Coordenadas del objetivo (si existe)
            cx, cy, x, y, w, h = 0, 0, 0, 0, 0, 0
            if best_contour is not None:
                estado_dron["ultimo_visto"] = time.time() 
                x, y, w, h = cv2.boundingRect(best_contour)
                cx, cy = x + w // 2, y + h // 2

            # ==========================================
            # MÁQUINA DE ESTADOS
            # ==========================================
            if estado_dron["modo"] == "HOVERING":
                if best_contour is not None:
                    if action_text == accion_en_mira:
                        conteo_frames += 1
                    else:
                        accion_en_mira = action_text
                        conteo_frames = 1
                    
                    if conteo_frames >= FRAMES_REQUERIDOS:
                        # Transición a TRACKING
                        estado_dron["modo"] = "TRACKING"
                        inicio_tracking = time.time()
                        accion_pendiente = accion_en_mira
                        print(f"\n[VISUAL SERVOING] Objetivo fijado. Siguiendo {accion_pendiente} por 3 segundos...")
                        
                        conteo_frames = 0
                        accion_en_mira = None
                else:
                    conteo_frames = 0
                    accion_en_mira = None
                    tiempo_inactivo = time.time() - estado_dron["ultimo_visto"]
                    
                    if tiempo_inactivo > 20:
                        print("\n[SEGURIDAD] 20 segundos sin detectar color. Aterrizaje automático.")
                        estado_dron["modo"] = "ATERRIZANDO"
                        break  
            
            elif estado_dron["modo"] == "TRACKING":
                action_text = f"TRACKING {accion_pendiente}..."
                
                if best_contour is not None:
                    # Lógica de Visual Servoing (Controlador Proporcional)
                    error_x = cx - CENTER_X
                    error_y = CENTER_Y - cy  # Positivo si el objetivo está arriba del centro

                    # Constantes de velocidad (Kp)
                    kp_yaw = 0.2
                    kp_up = 0.25

                    # Calculamos las velocidades y las limitamos (clip) para evitar movimientos bruscos
                    vel_yaw = int(np.clip(error_x * kp_yaw, -40, 40))
                    vel_up = int(np.clip(error_y * kp_up, -40, 40))

                    # Enviar comando al dron
                    tl_drone.flight.rc(a=0, b=0, c=vel_up, d=vel_yaw)

                    # Verificar si ya pasaron los 3 segundos
                    if (time.time() - inicio_tracking) >= 3.5:
                        print(f"\n[TRACKING] Completado. Deteniendo seguimiento e iniciando maniobra...")
                        tl_drone.flight.rc(a=0, b=0, c=0, d=0) # Frenar
                        estado_dron["modo"] = "MANIOBRANDO"
                        
                        if accion_pendiente == "VERTICAL SQUARE":
                            threading.Thread(target=ejecutar_cuadrado, args=(tl_drone,)).start()
                        elif accion_pendiente == "TORNADO":
                            threading.Thread(target=ejecutar_tornado, args=(tl_drone,)).start()
                        elif accion_pendiente == "CIRCLE":
                            threading.Thread(target=ejecutar_circulo, args=(tl_drone,)).start()
                        elif accion_pendiente == "LAND":
                            print("\n[VUELO] Señal de aterrizaje confirmada.")
                            estado_dron["modo"] = "ATERRIZANDO"
                            break
                else:
                    # Si perdemos el objetivo durante el tracking, abortamos por seguridad
                    print("\n[TRACKING] Objetivo perdido. Abortando seguimiento...")
                    tl_drone.flight.rc(a=0, b=0, c=0, d=0)
                    estado_dron["modo"] = "HOVERING"
                    
            elif estado_dron["modo"] == "MANIOBRANDO":
                action_text = "EJECUTANDO MANIOBRA..."
                draw_color = (0, 0, 255) 

            # ==========================================
            # DIBUJAR FEEDBACK VISUAL
            # ==========================================
            if best_contour is not None and estado_dron["modo"] in ["HOVERING", "TRACKING"]:
                cv2.rectangle(frame, (x, y), (x+w, y+h), draw_color, 2)
                cv2.circle(frame, (cx, cy), 5, draw_color, -1)
            
            # Textos generales UI
            cv2.putText(frame, f"Estado: {estado_dron['modo']}", (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 255, 255), 2)
            cv2.putText(frame, f"Accion: {action_text}", (10, 60), cv2.FONT_HERSHEY_SIMPLEX, 0.6, draw_color, 2)
            
            if estado_dron["modo"] == "HOVERING":
                if conteo_frames > 0:
                    cv2.putText(frame, f"Confirmando: {conteo_frames}/{FRAMES_REQUERIDOS}", (10, 90), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 255, 255), 2)
                tiempo_restante = 20 - (time.time() - estado_dron["ultimo_visto"])
                cv2.putText(frame, f"Timeout: {int(tiempo_restante)}s", (10, 120), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 255, 0), 2)

            # UI Especifica de Tracking
            if estado_dron["modo"] == "TRACKING":
                # Cruz central y línea hacia el objetivo
                cv2.drawMarker(frame, (CENTER_X, CENTER_Y), (0, 255, 0), markerType=cv2.MARKER_CROSS, markerSize=20, thickness=2)
                if best_contour is not None:
                    cv2.line(frame, (CENTER_X, CENTER_Y), (cx, cy), (0, 255, 255), 2)
                
                # Temporizador
                tiempo_restante_track = max(0.0, 3.0 - (time.time() - inicio_tracking))
                cv2.putText(frame, f"TRACKING: {tiempo_restante_track:.1f}s", (10, 90), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 255, 255), 2)

            cv2.imshow("Proyecto UAV - Drone Feed", frame)
            if cv2.waitKey(1) & 0xFF == ord('q'):
                break

    except KeyboardInterrupt:
        print("\nInterrupción manual detectada...")
        
    finally:
        print("\n[VUELO] Iniciando protocolo de aterrizaje y cierre...")
        try:
            tl_drone.flight.land().wait_for_completed()
            time.sleep(2) 
        except Exception as e:
            print(f"Error al aterrizar: {e}")
            
        tl_camera.stop_video_stream()
        cv2.destroyAllWindows()
        tl_drone.close()
        print("Protocolo finalizado. Adiós.")
        sys.exit(0)

if __name__ == '__main__':
    main()