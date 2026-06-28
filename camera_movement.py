from pyg import keyboard, camera

camera_speed = 6


possibles_zoom: list[float] = [0.25, 0.5, 1.0]
zoom_index: int = 2
zoom_level = possibles_zoom[zoom_index]


def horizontal_camera_movement(direction: int):
    camera.movement.x = direction * camera_speed


def vertical_camera_movement(direction: int):
    camera.movement.y = direction * camera_speed


def zoom():
    global zoom_level, zoom_index
    if zoom_index <= 0:
        return
    zoom_index -= 1
    zoom_level = possibles_zoom[zoom_index]


def unzoom():
    global zoom_level, zoom_index
    if zoom_index >= (possibles_zoom.__len__() - 1):
        return
    zoom_index += 1
    zoom_level = possibles_zoom[zoom_index]


keyboard.on_mouswheel_scroll(zoom, False)
keyboard.on_mouswheel_scroll(unzoom, True)


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
