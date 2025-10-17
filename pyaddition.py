import pygame


def is_even(numb: int):
    return numb % 2 == 0


def get_percentage(number: float, total: float):
    return number * 100 / total


class keyboard:
    pressed_keys = []
    clicks_pressed = []
    mouse_position = pygame.Vector2(0, 0)
    true_mouse_position = pygame.Vector2(0, 0)
    functions_to_execute_on_click = []
    click_map = {
        0: "left click",
        1: "right click",
        2: "middle click",
        3: "fourth click",  # the button on the side that's near the hand (fourth button)
        4: "fifth click",  # the button on the side that's far to the hand (fifth button)
    }

    clicks_pressed = (False, False, False, False, False)
    is_left_clicked_last_tick = False
    key_map_execute_on_step = {}
    key_map_execute_once = {}

    def key_press(key_number: int):
        key = pygame.key.name(key_number)
        keyboard.pressed_keys.append(key)

        if key in keyboard.key_map_execute_once.keys():

            function_to_execute: function = keyboard.key_map_execute_once[key][0]
            function_to_execute()

    def key_release(key):
        keyboard.pressed_keys.remove(pygame.key.name(key))

        if key in keyboard.key_map_execute_once.keys():
            function_to_execute_when_released: function = (
                keyboard.key_map_execute_on_step[key][1]
            )
            function_to_execute_when_released()

    def is_key_pressed(key: str):
        return key in keyboard.pressed_keys

    def step():

        keyboard.mouse_position = pygame.Vector2(
            pygame.mouse.get_pos()[0] + camera.rect.x,
            pygame.mouse.get_pos()[1] + camera.rect.y,
        )
        keyboard.true_mouse_position = pygame.Vector2(
            pygame.mouse.get_pos()[0],
            pygame.mouse.get_pos()[1],
        )
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

        keyboard.is_left_clicked_last_tick = (
            keyboard.click_map[0] in keyboard.pressed_keys
        )

        for key in keyboard.key_map_execute_on_step:
            if key in keyboard.key_press:
                function_to_execute_when_not_pressed: function = (
                    keyboard.key_map_execute_on_step[key][0]
                )
                function_to_execute_when_not_pressed()
            else:
                function_to_execute_when_not_pressed: function = (
                    keyboard.key_map_execute_on_step[key][1]
                )
                function_to_execute_when_not_pressed()

    class execute_on_click:
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

    def set_new_key_map(
        key: str,
        only_execute_function_one_time: bool,
        function_to_execute_when_press: "function",
        function_to_execute_when_not_pressed: "function" = None,
    ):
        if only_execute_function_one_time:
            keyboard.key_map_execute_once[key] = (
                function_to_execute_when_press,
                function_to_execute_when_not_pressed,
            )
        else:
            keyboard.key_map_execute_on_step[key] = (
                function_to_execute_when_press,
                function_to_execute_when_not_pressed,
            )


class camera:
    rect: pygame.Rect = None
    screen: pygame.Surface = None
    movement = pygame.Vector2((0, 0))

    def init():
        camera.rect = pygame.display.get_surface().get_rect()

    def step():
        camera.apply_movement()

    def apply_movement():
        camera.rect.x += camera.movement.x
        camera.rect.y += camera.movement.y

    def show(
        image: pygame.Surface,
        position: pygame.Rect | tuple[int, int],
        is_blocked_on_screen: bool = False,
    ):
        if isinstance(position, tuple):
            position = image.get_rect(x=position[0], y=position[1])

        if is_blocked_on_screen:  # it's globally a pg.blit
            pygame.display.get_surface().blit(image, position)
        else:
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


class Button:
    all_buttons = []
    true_mouse_pos = (0, 0)

    def init():
        Button.true_mouse_pos = pygame.mouse.get_pos()

    def __init__(
        self,
        image: pygame.Surface,
        function_to_execute_on_click: "function",
        x: int = 0,
        y: int = 0,
        width: int = 100,
        height: int = 100,
        *args_to_function
    ):
        self.x, self.y = x, y
        self.width, self.height = width, height

        self.image = pygame.transform.scale(image, (self.width, self.height))

        self.mask = pygame.mask.from_surface(self.image, 1)
        self.rect = self.mask.get_rect(x=self.x, y=self.y)

        self.function = function_to_execute_on_click
        self.args = args_to_function

        keyboard.functions_to_execute_on_click.append((self.on_click))
        self.is_alive = True
        Button.all_buttons.append(self)

    def destroy(self):
        Button.all_buttons.remove(self)

    def step(self):
        self.draw()

    def step_all():
        for button in Button.all_buttons:
            button: Button
            if button.is_alive:
                button.step()

    def draw(self):

        camera.show(self.image, (self.x, self.y), True)

    def on_click(self):
        if (
            self.is_alive
            and self.rect.collidepoint(keyboard.true_mouse_position)
            and self.mask.get_at(
                (
                    keyboard.true_mouse_position.x - self.x,
                    keyboard.true_mouse_position.y - self.y,
                )
            )
        ):  # if clicked the button (the rect checking is just for optimization)
            if self.args == None:
                self.function()
            else:
                self.function(*self.args)

    def is_position_in_zone_covered(
        x: int, y: int, is_position_relative: bool = True
    ) -> bool:
        if is_position_relative:
            x = x - camera.rect.x
            y = y - camera.rect.y
        for button in Button.all_buttons:
            button: Button
            if (
                button.is_alive
                and button.rect.collidepoint((x, y))
                and button.mask.get_at(
                    (
                        x - button.x,
                        y - button.y,
                    )
                )
            ):  # if clicked the button (the rect checking is just for optimization)
                return True
        return False


class draw:
    """class to get special surface easily"""

    def bar_percentage(
        percentage: float,
        width: int = 100,
        height: int = 25,
        bar_color: pygame.Color = "white",
        background_color: pygame.Color = None,
        border_size: int = 5,
        border_color: pygame.Color | str = "black",
    ) -> pygame.Surface:
        if border_size <= 0:
            raise ValueError("border size can't be less or equal to 0")

        output_surface = pygame.Surface(
            (width + border_size * 2, height + border_size * 2)
        )
        if background_color != None:
            output_surface.fill(background_color)

        pygame.draw.rect(
            output_surface,
            bar_color,
            pygame.Rect(0, 0, width * percentage / 100, height),
        )

        pygame.draw.rect(
            output_surface,
            border_color,
            output_surface.get_rect(),
            border_size,
        )

        return output_surface


def step_to_all_module():
    keyboard.step()
    Button.step_all()
    camera.step()


def init_all_module():
    Button.init()
    camera.init()


def print_time_of_function(function, *args, **kwds):
    import time

    start_time = time.time()
    function(*args, **kwds)
    end_time = time.time()
    print("time took=", end_time - start_time)
