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
