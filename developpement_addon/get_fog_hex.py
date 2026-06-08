import sys

sys.path.append("/home/louane/git/hexportes")

import pygame as pg
from hex import Hex
import data

number_of_fogs = 4
fog = data.load("assets/image/fog_map.png")

fog_hex = pg.Surface((Hex.width, Hex.height), pg.SRCALPHA)
fog = pg.transform.scale(fog, fog_hex.get_size())
hex_mask = Hex.mask


for x in range(fog_hex.get_width()):
    for y in range(fog_hex.get_height()):
        if hex_mask.get_at((x, y)):
            alpha = fog.get_at((x, y))[0]  # r==g==b so we just take r
            fog_hex.set_at((x, y), (0, 0, 0, alpha))


output_surface_path = "assets/hex_image/fog.png"
pg.image.save(fog_hex, output_surface_path)
