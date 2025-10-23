import pygame as pg

pg.display.init()
image = pg.image.load("assets/hex_stat/hex_stat_when_mouse_not_on_it/hex.png")

print(image.get_alpha())
image = image.convert(image)
print(image.get_alpha())
