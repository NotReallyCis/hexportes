import pygame


class keyboard:

    pressed_keys = []
    clicks_pressed = []
    mouse_position = pygame.Vector2(pygame.mouse.get_pos())
    function_to_execute_on_click = []
    click_map = {
        0: "left click",
        1: "right click",
        2: "middle click",
        3: "fourth click",  # the button on the side that's near the hand (fourth button)
        4: "fifth click",  # the button on the side that's far to the hand (fifth button)
    }

    def key_press(key):
        keyboard.pressed_keys.append(pygame.key.name(key))

    def key_release(key):
        keyboard.pressed_keys.remove(pygame.key.name(key))

    def step():

        keyboard.mouse_position = pygame.Vector2(pygame.mouse.get_pos())
        global clicks_pressed
        clicks_pressed = pygame.mouse.get_pressed(5)

        for click_checked in range(5):

            if clicks_pressed[click_checked]:
                if keyboard.click_map[click_checked] not in keyboard.pressed_keys:
                    keyboard.pressed_keys.append(keyboard.click_map[click_checked])

            elif keyboard.click_map[click_checked] in keyboard.pressed_keys:
                keyboard.pressed_keys.remove(keyboard.click_map[click_checked])

        if keyboard.click_map[0] in keyboard.pressed_keys:  # if left button is pressed
            for function in keyboard.function_to_execute_on_click:
                function()

    def execute_on_clik(function):
        """execute automaticly the function when the left mouse button is clicked, it can't take argument nor output the result of the function"""
        keyboard.function_to_execute_on_click.append(function)

        return function


class camera:

    rect = pygame.display.get_surface().get_rect()

    screen = pygame.Surface((rect.width, rect.height))

    def reset_screen():  # must be called
        camera.screen.fill("black")

    def show_on_camera(image: pygame.Surface, position: pygame.Rect | tuple[int, int]):
        if isinstance(position, tuple):
            position = image.get_rect(x=position[0], y=position[1])

        relative_destination = pygame.Rect(
            position.x - camera.rect.x,
            position.y - camera.rect.y,
            position.width,
            position.height,
        )

        if camera.rect.colliderect(
            position
        ):  # check if it's in the screen (optimization)
            pygame.display.get_surface().blit(image, relative_destination)


def is_even(numb: int):
    return numb % 2 == 0
