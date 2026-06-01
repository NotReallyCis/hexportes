import pygame as pg
import pyg, warnings


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


######## sound #######


pg.mixer.init()
selected_bad_unit_sound = pg.mixer.Sound("assets/sound/confirm_style_4_004.wav")


###### unit type ######

directory_unit_team_color = "assets/unit_with_team_color" + "/"


### hex_type ###


# FIXME: this shit is definitly doing some weird things
class hex_type:
    import math

    size = 35  # size of one side of an hex
    width = math.sqrt(3) * size  # pythagorean theorem
    height = 2 * size  # and that comes from a website

    folder_str_mouse_not_on_it = "assets/hex_stat/hex_stat_when_mouse_not_on_it"
    folder_str_mouse_on_it = "assets/hex_stat/hex_stat_when_mouse_on_it"

    DEFAULT = "hex.png"
    UNIT_CAN_GO = "hex_can_go.png"
    UNIT_CAN_ATTACK = "hex_can_attack.png"

    luminosity_added_when_mouse_on_hex = 50
    mouse_on_it_image_mask = pg.Surface((width, height))
    """To add to an image with pg.BLEND_RGB_ADD to make it look selected"""
    mouse_on_it_image_mask.fill(
        pg.Color(
            luminosity_added_when_mouse_on_hex,
            luminosity_added_when_mouse_on_hex,
            luminosity_added_when_mouse_on_hex,
        )
    )

    image_types = get_all_image_in_folder(folder_str_mouse_not_on_it)
    for key in image_types:
        image = image_types[key]
        image = pg.transform.scale(image, (width, height))
        image_types[key] = image
    types_mouse_on_it = get_all_image_in_folder(folder_str_mouse_on_it)

    @classmethod
    @pyg.Profiler
    def get_hex_image_from_stat(  # FIXME: performance bottleneck
        cls, stat: str, is_mouse_on_it: bool, is_visible: bool
    ) -> pg.Surface:

        output_surface = hex_type.image_types[stat].copy()

        if is_mouse_on_it:
            output_surface.blit(
                hex_type.mouse_on_it_image_mask,
                (0, 0),
                special_flags=pg.BLEND_ADD,
            )

        if not is_visible:
            output_surface.blit(
                fog,
                (0, 0),
                special_flags=pg.BLEND_ADD,
            )

        return output_surface


### image ###

fog = load("assets/image/fog_hex.png")


hex_highlight = load("assets/essentials-4xgames-tileset/tile-farm-sown.png")

hex_image = load("assets/hex_stat/hex_stat_when_mouse_not_on_it/hex.png")

next_turn_button = load("assets/image/end_turn_button.png")

go_button = load("assets/image/go_button.png")
attack_button = load("assets/image/attack_button.png")

if pg.display.get_active():
    background_waiting_image = pg.transform.scale(
        load("assets/image/placeholder_image_waiting.png"),
        pg.display.get_surface().get_size(),
    )

fuel_icon = load("assets/image/fuel_icon.png")


### click stat ###
class click_stat:
    """this class is used to define the different stat of action done when a click occurs"""

    SELECT_UNIT = "select_unit"
    SELECT_UNIT_DESTINATION = "select_unit_destination"
    SELECT_UNIT_ATTACK = "select_unit_to_attack"
    stat = None
