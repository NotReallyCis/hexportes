map_of_key = {
    "up": "z",
    "down": "s",
    "left": "q",
    "right": "d",
    "end_of_turn": "f5",
}

from pyaddition import keyboard


def is_command_pressed(command: str):
    return keyboard.is_key_pressed(map_of_key[command])


def create_function_on_command(
    command: str, function: "function", execute_only_once: bool = True
):
    keyboard.set_new_key_map(
        map_of_key[command],
        execute_only_once,
        function,
    )
