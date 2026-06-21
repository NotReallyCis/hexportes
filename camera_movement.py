from pyg import keyboard, camera

camera_speed = 6


zoom_level = 1
min_zoom = 0.1
max_zoom = 100


def horizontal_camera_movement(direction: int):
    camera.movement.x = direction * camera_speed


def vertical_camera_movement(direction: int):
    camera.movement.y = direction * camera_speed


def zoom():
    global zoom_level
    if zoom_level < min_zoom:
        return
    zoom_level /= 2


def unzoom():
    global zoom_level
    if zoom_level > max_zoom:
        return
    zoom_level *= 2


keyboard.on_mouswheel_scroll(zoom, True)
keyboard.on_mouswheel_scroll(unzoom, False)


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
