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


def create_function_on_key_map(
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

directory_unit_team_color = "assets/unit_with_team_color" + "/"


### hex_type ###


class hex_type:
    import math

    size = 35  # size of one side of an hex
    width = math.sqrt(3) * size  # pythagorean theorem
    height = 2 * size  # and that comes from a website

    luminosity_added_when_mouse_on_hex = 40

    folder_str_mouse_not_on_it = "assets/hex_stat/hex_stat_when_mouse_not_on_it"
    folder_str_mouse_on_it = "assets/hex_stat/hex_stat_when_mouse_on_it"

    def get_all_image_in_folder(folder_str: str):
        """the return format is a dict with filename (relative to the folder):image"""
        import os

        output = {}
        folder = os.fsencode(folder_str)
        for file in os.listdir(folder):
            file_name = os.fsdecode(file)
            output[file_name] = pg.image.load(
                folder_str + "/" + file_name
            ).convert_alpha()
        return output

    DEFAULT = "hex.png"
    UNIT_CAN_GO = "hex_can_go.png"
    UNIT_CAN_ATTACK = "hex_can_attack.png"

    types_mouse_not_on_it = get_all_image_in_folder(folder_str_mouse_not_on_it)
    for key in types_mouse_not_on_it:
        image = types_mouse_not_on_it[key]
        image = pg.transform.scale(image, (width, height))
        types_mouse_not_on_it[key] = image
    types_mouse_on_it = get_all_image_in_folder(folder_str_mouse_on_it)

    def get_hex_image_from_stat(
        stats: list, is_mouse_on_it: bool, is_visible: bool
    ) -> pg.Surface:
        output_surface = pg.Surface((hex_type.width, hex_type.height))
        output_surface.set_colorkey(pg.Color(0, 0, 0))  # transparent

        if stats == []:
            if not is_mouse_on_it:
                output_surface.blit(
                    hex_type.types_mouse_not_on_it[hex_type.DEFAULT], (0, 0)
                )
            else:
                output_surface.blit(
                    hex_type.types_mouse_on_it[hex_type.DEFAULT], (0, 0)
                )

        else:
            for stat in stats:
                if not is_mouse_on_it:
                    output_surface.blit(hex_type.types_mouse_not_on_it[stat], (0, 0))
                else:
                    output_surface.blit(hex_type.types_mouse_on_it[stat], (0, 0))

        if not is_visible:
            output_surface = output_surface.copy()
            output_surface.blit(
                fog,
                (0, 0),
                special_flags=pg.BLEND_ADD,
            )
        return output_surface


### image ###

fog = pg.image.load("assets/image/fog_hex.png").convert_alpha()


hex_highlight = pg.image.load(
    "assets/essentials-4xgames-tileset/tile-farm-sown.png"
).convert_alpha()

hex_image = pg.image.load(
    "assets/hex_stat/hex_stat_when_mouse_not_on_it/hex.png"
).convert_alpha()

next_turn_button = pg.image.load("assets/image/end_turn_button.png").convert_alpha()

go_button = pg.image.load("assets/image/go_button.png").convert_alpha()
attack_button = pg.image.load("assets/image/attack_button.png").convert_alpha()

background_waiting_image = pg.image.load(
    "assets/image/placeholder_image_waiting.png"
).convert_alpha()

fuel_icon = pg.image.load("assets/image/fuel_icon.png").convert_alpha()

### map ###

empty_map_str = open("developpement_addon/map.txt", "r").read()


### click stat ###
class click_stat:
    """this class is used to define the different stat of action done when a click occurs"""

    SELECT_UNIT = "select_unit"
    SELECT_UNIT_MOVEMENT = "select_unit_destination"
    SELECT_UNIT_ATTACK = "select_unit_to_attack"
    SELECT_UNIT_CREATION = "select_unit_creation"
    stat = None
