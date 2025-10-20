import pygame as pg
import data

RANGE = "range"
VIEW_RANGE = "view_range"

MOVEMENT_POINT = "movement_point"
IMAGE = "image"
PV = "pv"
DAMAGE = "damage"
AMMO = "ammo"
FUEL = "fuel"

MATERIAL = "material"
CREATABLE_UNIT = "creatable_unit"

TEST_UNIT = "first_test"
TEST_USINE = "usine_test"

TYPE_UNIT = "Unit"
TYPE_USINE = "Usine"

object_type = {
    TEST_UNIT: {
        MOVEMENT_POINT: 4,
        RANGE: 5,
        VIEW_RANGE: 5,
        IMAGE: "tile-animal-cow.png",
        PV: 10,
        DAMAGE: 5,
        AMMO: 10,
        FUEL: 10,
    },
    TEST_USINE: {
        VIEW_RANGE: 5,
        IMAGE: "tile-village.png",
        PV: 15,
        MATERIAL: 10,
        CREATABLE_UNIT: [TEST_UNIT],
    },
}


def get_unit_image_by_unit_and_color(unit_name: str, color: str):
    image_name = object_type[unit_name][IMAGE]
    return pg.image.load(
        data.directory_unit_team_color + color + "_" + image_name
    ).convert_alpha()
