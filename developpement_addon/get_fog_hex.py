import sys

sys.path.append("C:/Users/bauma/Documents/GitHub/hexportes")


import data
import pygame as pg

fog = pg.image.load("assets/image/fog_map.png")
hex_image = data.hex_image
hex_image = hex_image.copy()
hex_image = pg.transform.scale(hex_image, (data.hex_type.width, data.hex_type.height))
hex_mask = pg.mask.from_surface(hex_image, 1)
output_surface_path = "assets/image/fog_hex.png"


output_surface = pg.Surface(
    (data.hex_type.width, data.hex_type.height), flags=pg.SRCALPHA
)
for x in range(output_surface.get_width()):
    for y in range(output_surface.get_height()):

        if hex_mask.get_at((x, y)):
            output_surface.set_at((x, y), fog.get_at((x, y)))

pg.image.save(output_surface, output_surface_path)
