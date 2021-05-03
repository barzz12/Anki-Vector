import time
import math
import anki_vector

with anki_vector.Robot() as robot:
    print("disconnecting from any connected cube...")
    robot.world.disconnect_cube()

    time.sleep(2)

    print("connect to a cube...")
    connectionResult = robot.world.connect_cube()
    connected_cube = robot.world.connected_light_cube

    connected_cube.set_light_corners(anki_vector.lights.blue_light,
                                     anki_vector.lights.off_light,
                                     anki_vector.lights.red_light,
                                     anki_vector.lights.off_light)

    print("For the next 8 seconds, please tap and move the cube. Cube properties will be logged to console.")
    for _ in range(16000):
        #connected_cube = robot.world.connected_light_cube
        if connected_cube:
            print("-----------------------")
            if connected_cube.top_face_orientation_rad:
                angle = connected_cube.top_face_orientation_rad * (180 / math.pi)
                print(f'top_face_orientation_rad: {angle}')
            else:
                print(f'top_face_orientation_rad: {connected_cube.top_face_orientation_rad}')
            #1577975347.1891317

            print(f'last_tapped_time: {connected_cube.last_tapped_robot_timestamp}')
            print(f'up_axis : {connected_cube.up_axis}')
            print(f'moving : {connected_cube.is_moving}')
            print(f'connect : {connected_cube.is_connected}')
            print("-----------------------\n")

        time.sleep(0.5)
