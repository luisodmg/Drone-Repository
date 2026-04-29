from djitellopy import Tello
import cv2
import time
import os

# Save the video in the same folder as this script (Third-Practice/)
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
OUTPUT_FILE = os.path.join(SCRIPT_DIR, "circle_flight.mp4")
FPS = 30
RESOLUTION = (960, 720)   # Tello default stream resolution

if __name__ == '__main__':
    tl_drone = Tello()
    tl_drone.connect()

    # Check battery before takeoff
    battery = tl_drone.get_battery()
    print(f"Battery: {battery}%")
    if battery < 15:
        print("Battery too low to fly safely.")
        tl_drone.end()
        exit()

    # Open camera resources
    tl_drone.streamon()
    frame_read = tl_drone.get_frame_read()

    # Initialize video writer — saves as .mp4
    fourcc = cv2.VideoWriter_fourcc(*'mp4v')
    out = cv2.VideoWriter(OUTPUT_FILE, fourcc, FPS, RESOLUTION)

    # Take off
    tl_drone.takeoff()
    time.sleep(2)

    print(f"Recording video to '{OUTPUT_FILE}' — performing circular trajectory...")

    # Circular trajectory parameters (same as circular_trajectory.py)
    YAW_SPEED = 30
    FORWARD_SPEED = 20   # lower = smaller circle
    steps = 72
    step_duration = 0.33  # seconds per step

    for _ in range(steps):
        tl_drone.send_rc_control(0, FORWARD_SPEED, 0, YAW_SPEED)

        # Record frame on every rc step
        img = frame_read.frame
        img_resized = cv2.resize(img, RESOLUTION)
        out.write(img_resized)
        cv2.imshow("Drone (recording)", img_resized)
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

        time.sleep(step_duration)

    # Stop all motion — mandatory after rc commands
    tl_drone.send_rc_control(0, 0, 0, 0)
    time.sleep(2)

    cv2.destroyAllWindows()

    # Land before releasing resources
    tl_drone.land()

    # Release video writer and camera resources
    out.release()
    tl_drone.streamoff()
    tl_drone.end()

    print(f"Video saved to '{OUTPUT_FILE}'")
