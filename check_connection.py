import robomaster
from robomaster import robot


if __name__ == '__main__':
    tl_drone = robot.Drone()
    tl_drone.initialize()

    # Get the SDK of the QUAV.
    drone_version = tl_drone.get_sdk_version()
    print("Drone sdk version: {0}".format(drone_version))

    tl_battery = tl_drone.battery

    battery_info = tl_battery.get_battery()
    print(f"Batería actual del dron: {battery_info}%")

    tl_drone.close()