import pygame


class keyboard:

    pressed_keys = []
    clicks_pressed = []
    mouse_position = pygame.Vector2(pygame.mouse.get_pos())
    functions_to_execute_on_click = []
    click_map = {
        0: "left click",
        1: "right click",
        2: "middle click",
        3: "fourth click",  # the button on the side that's near the hand (fourth button)
        4: "fifth click",  # the button on the side that's far to the hand (fifth button)
    }

    clicks_pressed = pygame.mouse.get_pressed(5)
    is_left_clicked_last_tick = False

    def key_press(key):
        keyboard.pressed_keys.append(pygame.key.name(key))

    def key_release(key):
        keyboard.pressed_keys.remove(pygame.key.name(key))

    def step():

        keyboard.mouse_position = pygame.Vector2(pygame.mouse.get_pos())
        keyboard.clicks_pressed = pygame.mouse.get_pressed(5)

        for click_currently_checking in range(5):

            if keyboard.clicks_pressed[click_currently_checking]:
                if (
                    keyboard.click_map[click_currently_checking]
                    not in keyboard.pressed_keys
                ):
                    keyboard.pressed_keys.append(
                        keyboard.click_map[click_currently_checking]
                    )

            elif keyboard.click_map[click_currently_checking] in keyboard.pressed_keys:
                keyboard.pressed_keys.remove(
                    keyboard.click_map[click_currently_checking]
                )

        keyboard.execute_all_function_if_click()

        if keyboard.click_map[0] in keyboard.pressed_keys:
            keyboard.is_left_clicked_last_tick = True
        else:
            keyboard.is_left_clicked_last_tick = False

    class execute_on_clik:
        """execute automaticly the function when the left mouse button is clicked, it can't take argument nor output the result of the function"""

        def __init__(self, function):
            if function not in keyboard.functions_to_execute_on_click:
                keyboard.functions_to_execute_on_click.append(function)

        def __call__(self, function, *args, **kwds):
            function(*args, **kwds)

    def execute_all_function_if_click():

        if (
            keyboard.click_map[0] in keyboard.pressed_keys
            and not keyboard.is_left_clicked_last_tick
        ):  # if left button is pressed
            for function in keyboard.functions_to_execute_on_click:
                function()


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


class Button:
    all_buttons = []

    def __init__(
        self,
        image: pygame.Surface,
        function_to_execute_on_click,
        x: int = 0,
        y: int = 0,
        width: int = 100,
        height: int = 100,
    ):
        self.x, self.y = x, y
        self.width, self.height = width, height

        self.image = pygame.transform.scale(image, (self.width, self.height))

        self.mask = pygame.mask.from_surface(self.image, 1)
        self.rect = self.mask.get_rect()

        self.function = function_to_execute_on_click

        Button.all_buttons.append(self)

        keyboard.functions_to_execute_on_click.append((self.on_click))

    def destroy(self):
        Button.all_buttons.remove(self)

    def step(self):
        self.draw()

    def step_all():
        for button in Button.all_buttons:
            button: Button
            button.step()

    def draw(self):

        camera.show_on_camera(self.image, (self.x, self.y))

    def on_click(self):
        if self.rect.collidepoint(keyboard.mouse_position) and self.mask.get_at(
            keyboard.mouse_position
        ):  # if clicked the button (the rect checking is just for optimization)
            self.function()


def step_to_all_module():
    keyboard.step()
    Button.step_all()
