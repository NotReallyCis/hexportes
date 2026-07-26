import pygame as pg
import pyg, warnings, json


def get_all_image_in_folder(folder_str: str):
    """the return format is a dict with filename (relative to the folder):image"""
    import os

    output: dict[str, pg.Surface] = {}
    folder = os.fsencode(folder_str)
    for file in os.listdir(folder):
        file_name = os.fsdecode(file)
        output[file_name] = load(folder_str + "/" + file_name)
    return output


def load(
    path: str,
    colorkey: tuple[int, int, int] = None,
    size: tuple[int, int] = None,
    in_asset: bool = True,
    end: str = ".png",
):
    """an elegant pg.image.load"""
    if in_asset and not path.startswith("assets/"):
        path = "assets/" + path

    if not path.endswith(end):
        path += end

    output = pg.image.load(path)
    if colorkey is not None:
        output.set_colorkey(colorkey)
    if size is not None:
        output = pg.transform.scale(output, size)
    if pg.display.get_active():
        return output.convert_alpha()
    else:
        warnings.warn(
            "The Display wasn't initiated before data was imported", ImportWarning
        )
        return output


####### teams color ######


color_of_teams = {
    (64, 106, 150): "blue",
    (213, 88, 88): "red",
    (77, 170, 90): "green",
}


def get_all_colors():
    output :list[str]= []
    for color in color_of_teams:
        output.append(color_of_teams[color])
    return output


all_colors = get_all_colors()


######## sound #######


pg.mixer.init()
selected_bad_unit_sound = pg.mixer.Sound("assets/sound/confirm_style_4_004.wav")


###### unit type ######

directory_unit_team_color = "assets/unit_with_team_color/"

### image ###

BAREN = "baren terrain"
OIL = "oil field terrain"
GREEN = "green terrain"
ROCKY = "rocky terrain"
WATER = "water terrain"


baren = load("hex_image/base_baren")
oil = load("hex_image/oil_baren")
green = load("hex_image/base_green")
rocky = load("hex_image/base_rocky")
water = load("hex_image/base_watery")

try:
    map = json.load(open("assets/map.json"))
except json.decoder.JSONDecodeError:
    map = None
fog = load("assets/hex_image/fog.png")

hex_image = load("essentials-4xgames-tileset/base_rocky.png")
"""The default hex image for mask or other things"""

next_turn_button = load("assets/image/end_turn_button.png")

go_button = load("assets/image/go_button.png")
attack_button = load("assets/image/attack_button.png")
transport_button = load("assets/image/transport_button")
fabricate_unit_background_button = load(
    "image/background_selected_unit_to_fabricate_button"
)

nine_sided_explanation = pyg.draw.Nine_sided_rect(
    pg.Color(255, 253, 245),
    load("image/explanation_rect/bottom"),
    load("image/explanation_rect/top"),
    load("image/explanation_rect/left"),
    load("image/explanation_rect/right"),
    load("image/explanation_rect/corner_left"),
    load("image/explanation_rect/corner_right"),
    load("image/explanation_rect/corner_bottom_left"),
    load("image/explanation_rect/corner_bottom_right"),
)

hex_mouse_on = load("image/mouse_on_tile")
hex_can_go = load("image/can_go_tile")
hex_can_attack = load("image/can_attack_tile")
hex_can_fabricate = load("image/can_fabricate_tile")
hex_can_transport = load("image/can_transport_tile")


if pg.display.get_active():
    background_waiting_image = pg.transform.scale(
        load("assets/image/placeholder_image_waiting.png"),
        pg.display.get_surface().get_size(),
    )

### click stat ###
current_state = None


class click_state:
    """this class is used to define the different stat of action done when a click occurs"""

    SELECT_UNIT = "select_unit"
    MAP_BUILDING = "MAP_BUILDING"
