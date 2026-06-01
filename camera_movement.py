from pyg import keyboard, camera

camera_speed = 6


def horizontal_camera_movement(direction: int):
    camera.movement.x = direction * camera_speed


def vertical_camera_movement(direction: int):
    camera.movement.y = direction * camera_speed


def step():
    if keyboard.is_key_pressed("z"):
        vertical_camera_movement(-1)
    elif keyboard.is_key_pressed("s"):
        vertical_camera_movement(1)
    else:
        vertical_camera_movement(0)

    if keyboard.is_key_pressed("q"):
        horizontal_camera_movement(-1)
    elif keyboard.is_key_pressed("d"):
        horizontal_camera_movement(1)
    else:
        horizontal_camera_movement(0)
