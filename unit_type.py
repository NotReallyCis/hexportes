import pygame as pg
import data

RANGE = "range"
VIEW_RANGE = "view_range"

MOVEMENT_POINT = "movement_point"
IMAGE = "image"
PV = "pv"
TEST_UNIT = "first_test"
DAMAGE = "damage"
AMMO = "ammo"
FUEL = "fuel"

unit_type = {
    TEST_UNIT: {
        MOVEMENT_POINT: 4,
        RANGE: 5,
        VIEW_RANGE: 5,
        IMAGE: "tile-village.png",
        PV: 10,
        DAMAGE: 5,
        AMMO: 10,
        FUEL: 10,
    },
}


def get_unit_image_by_unit_and_color(unit_name: str, color: str):
    image_name = unit_type[unit_name][IMAGE]
    return pg.image.load(data.directory_unit_team_color + color + "_" + image_name)
