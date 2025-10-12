####### teams color ######


color_of_teams = {
    (255, 0, 0): "red",
    (0, 255, 0): "green",
    (0, 0, 255): "blue",
}


def get_all_colors():
    output = []
    for color in color_of_teams:
        output.append(color_of_teams[color])
    return output


all_colors = get_all_colors()


######## key map ########

map_of_key = {
    "up": "z",
    "down": "s",
    "left": "q",
    "right": "d",
    "end_of_turn": "f5",
}

from pyaddition import keyboard


def is_command_pressed(command: str):
    return keyboard.is_key_pressed(map_of_key[command])


def create_function_on_command(
    command: str, function: "function", execute_only_once: bool = True
):
    keyboard.set_new_key_map(
        map_of_key[command],
        execute_only_once,
        function,
    )


######## sound #######


import pygame as pg

pg.mixer.init()
selected_bad_unit_sound = pg.mixer.Sound("assets/sound/confirm_style_4_004.wav")


###### unit type ######


import pygame as pg

MOVEMENT_POINT = "movement_point"
IMAGE = "image"

TEST_UNIT = "first_test"


unit_type = {
    TEST_UNIT: {
        MOVEMENT_POINT: 4,
        IMAGE: "tile-village.png",
    },
}


""" format look like this:
    TEST = {
        MOVEMENT_POINT: 0,
        IMAGE: ".png"
    }
"""

directory_unit_team_color = "assets/unit_with_team_color" + "/"


def get_unit_image_by_unit_and_color(unit_name: str, color: str):
    image_name = unit_type[unit_name][IMAGE]
    return pg.image.load(directory_unit_team_color + color + "_" + image_name)


### image ###

hex_highlight = pg.image.load("assets/essentials-4xgames-tileset/tile-farm-sown.png")

hex_image = pg.image.load("assets/image/hex_placeholder.png")

next_turn_button = pg.image.load(
    "assets/Complete_UI_Essential_Pack_Free/Complete_UI_Essential_Pack_Free/01_Flat_Theme/Sprites/UI_Flat_IconCheck01a.png"
)

background_waiting_image = pg.image.load("assets/image/placeholder_image_waiting.png")

possible_paths_marker_image_for_unit = pg.image.load(
    "assets/essentials-4xgames-tileset/base_watery.png"
)

### map ###

empty_map_str = open("developpement_addon\map.txt", "r").read()
