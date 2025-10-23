import pygame as pg

TYPE = "type"
NAME = "name"
TEAM = "team"
RANGE = "range"
VIEW_RANGE = "view_range"
MOVEMENT_POINT = "movement_point"
IMAGE = "image"
PV = "pv"
DAMAGE = "damage"
AMMO = "ammo"
FUEL = "fuel"
COST = "cost"
MATERIAL = "material"
CREATABLE_UNIT = "creatable_unit"
MOVEMENT_POINT_NEEDED = "movement_point_needed"
BUTTON_IMAGE = "button"

TEST_UNIT = "first_test"
TEST_UNIT2 = "second_test"
TEST_USINE = "usine_test"

TYPE_UNIT = "Unit"
TYPE_USINE = "Usine"
TYPE_OBJECT = "Object"

object_type = {
    TEST_UNIT: {
        MOVEMENT_POINT: 4,
        RANGE: 5,
        VIEW_RANGE: 5,
        IMAGE: "tile-animal-cow.png",
        PV: 10,
        DAMAGE: 5,
        AMMO: 10,
        FUEL: 35,
        MOVEMENT_POINT_NEEDED: 2,
        COST: 5,
    },
    TEST_UNIT2: {
        MOVEMENT_POINT: 2,
        RANGE: 5,
        VIEW_RANGE: 5,
        IMAGE: "tile-animal-pig.png",
        PV: 20,
        DAMAGE: 10,
        AMMO: 40,
        FUEL: 50,
        MOVEMENT_POINT_NEEDED: 2,
        COST: 10,
    },
    TEST_USINE: {
        VIEW_RANGE: 5,
        IMAGE: "tile-village.png",
        PV: 15,
        MATERIAL: 10,
        CREATABLE_UNIT: [TEST_UNIT, TEST_UNIT2],
        MOVEMENT_POINT_NEEDED: 5,
        COST: 20,
    },
}


def get_object_image_by_name_and_color(unit_name: str, color: str):
    import data

    image_name = object_type[unit_name][IMAGE]
    return pg.image.load(
        data.directory_unit_team_color + color + "_" + image_name
    ).convert_alpha()


def get_class_by_type_name(type_name: str):
    import unit

    if type_name == TYPE_OBJECT:
        return unit.Object
    elif type_name == TYPE_UNIT:
        return unit.Unit
    elif type_name == TYPE_USINE:
        return unit.Usine
    else:
        raise ValueError(type_name, "is not recognized as a type name")


import developpement_addon.create_button

developpement_addon.create_button.create_button_for_each_unit()
