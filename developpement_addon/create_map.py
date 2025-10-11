import sys

sys.path.append("C:/Users/bauma/Documents/GitHub/hexportes")

import Hex, json

map_txt = open("developpement_addon/map.txt", "w")

Hex.Hex.create_hexs_map()
map = Hex.Hex.get_all_hexs__str__()

print(json.dumps(map))
map_txt.write(json.dumps(map))
print("map created!")
