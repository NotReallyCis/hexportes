from data import is_command_pressed
from pyaddition import keyboard, camera

camera_speed = 4


def horizontal_camera_movement(direction: "int[-1, 0, 1]"):
    camera.movement.x = direction * camera_speed


def vertical_camera_movement(direction: "int[-1, 0, 1]"):
    camera.movement.y = direction * camera_speed


def step():
    if is_command_pressed("up"):
        vertical_camera_movement(-1)
    elif is_command_pressed("down"):
        vertical_camera_movement(1)
    else:
        vertical_camera_movement(0)

    if is_command_pressed("left"):
        horizontal_camera_movement(-1)
    elif is_command_pressed("right"):
        horizontal_camera_movement(1)
    else:
        horizontal_camera_movement(0)
