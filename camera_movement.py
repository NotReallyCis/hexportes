from pyg import keyboard, camera
import pygame as pg
import pyg

camera_speed = 6


possibles_zoom: list[float] = [0.25, 0.5, 1.0]
zoom_index: int = 2
zoom_level = possibles_zoom[zoom_index]


def horizontal_camera_movement(direction: int):
    camera.movement.x = direction * camera_speed


def vertical_camera_movement(direction: int):
    camera.movement.y = direction * camera_speed


def zoom(is_unzoom: bool):
    global zoom_level, zoom_index
    global_mouse_pos_old = keyboard.mouse_position / zoom_level

    if is_unzoom:
        if zoom_index >= (possibles_zoom.__len__() - 1):
            return
        zoom_index += 1
    else:
        if zoom_index <= 0:
            return
        zoom_index -= 1
    zoom_level = possibles_zoom[zoom_index]

    camera.rect.topleft = (
        global_mouse_pos_old * zoom_level
    ) - keyboard.true_mouse_position  # complicated af, don't touch this


keyboard.on_mouswheel_scroll(zoom, False, False)
keyboard.on_mouswheel_scroll(zoom, True, True)


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
