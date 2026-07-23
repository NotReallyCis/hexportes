import sys, json, random

sys.path.append("/home/louane/git/hexportes")
from hex import Hex

map_file = open("assets/map.json", "w")

possible_terrain = list(Hex.terrain_types.keys())


def get_random_terrain():
    random_map: list["str"] = []
    for _ in range(Hex.map_width * Hex.map_height):
        random_map.append(random.choice(possible_terrain))
    return random_map


def write_map_to_file(map: list[str]):
    map_file.write(
        json.dumps(
            map,
        )
    )


write_map_to_file(get_random_terrain())
