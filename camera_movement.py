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
    old_zoom = zoom_level

    if is_unzoom:
        if zoom_index >= (possibles_zoom.__len__() - 1):
            return
        zoom_index += 1
    else:
        if zoom_index <= 0:
            return
        zoom_index -= 1
    zoom_level = possibles_zoom[zoom_index]
    zoomed_camera_rect: pg.Rect = camera.rect.copy()
    if is_unzoom:
        bottom_right = zoomed_camera_rect.bottomright
        zoomed_camera_rect.scale_by_ip(zoom_level, zoom_level)
        zoomed_camera_rect.topleft = bottom_right
    else:
        topleft = zoomed_camera_rect.topleft
        zoomed_camera_rect.scale_by_ip(zoom_level, zoom_level)
        zoomed_camera_rect.topleft = topleft

    old_zoomed_camera_rect = camera.rect.copy()
    if is_unzoom:
        bottom_right = zoomed_camera_rect.bottomright
        old_zoomed_camera_rect.scale_by_ip(old_zoom, old_zoom)
        old_zoomed_camera_rect.topleft = bottom_right
    else:
        topleft = zoomed_camera_rect.topleft
        old_zoomed_camera_rect.scale_by_ip(old_zoom, old_zoom)
        old_zoomed_camera_rect.topleft = topleft

    camera.rect.x -= (
        keyboard.mouse_position.x
        / camera.rect.width
        * (old_zoomed_camera_rect.width - zoomed_camera_rect.width)
    )
    camera.rect.y -= (
        keyboard.mouse_position.y
        / camera.rect.height
        * (old_zoomed_camera_rect.height - zoomed_camera_rect.height)
    )


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
