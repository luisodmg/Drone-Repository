from djitellopy import Tello
import cv2
import time


# FRAMES_TO_SHOW = 300

if __name__ == "__main__":
    tello = Tello()
    tello.connect()

    # Open camera resources
    tello.streamon()
    time.sleep(2)           # wait for UDP video stream to initialize
    frame_read = tello.get_frame_read()

    # Stream camera continuously until 'q' is pressed
    while True:
        img = frame_read.frame
        img_bgr = cv2.cvtColor(img, cv2.COLOR_RGB2BGR)
        cv2.imshow("Drone", img_bgr)
        if cv2.waitKey(1) & 0xFF == ord("q"):
            break

    cv2.destroyAllWindows()

    # Release camera resources
    tello.streamoff()
    tello.end()