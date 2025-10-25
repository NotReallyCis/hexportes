import sys

sys.path.append("C:/Users/bauma/Documents/GitHub/hexportes")


import object_type
import pygame as pg


def create_button_for_each_unit():
    background_image = pg.image.load(
        "assets/Complete_UI_Essential_Pack_Free/Complete_UI_Essential_Pack_Free/01_Flat_Theme/Sprites/UI_Flat_Banner01a.png"
    )
    rect_to_draw_text_on = pg.Rect(10, 7, 43, 9)  # relative to the image
    font = pg.font.Font(pg.font.get_default_font(), rect_to_draw_text_on.height)
    text_color = "black"

    for unit_name in object_type.object_type:
        button_image = background_image.copy()
        text = font.render(unit_name, 0, text_color)
        button_image.blit(text, rect_to_draw_text_on)
        object_type.object_type[unit_name][object_type.BUTTON_IMAGE] = Image(
            button_image
        )
