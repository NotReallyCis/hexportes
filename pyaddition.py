import pygame as pg


def is_even(numb: int):
    return numb % 2 == 0


def get_percentage(number: float, total: float):
    return number * 100 / total


def is_two_surfaces_equal(surface1: pg.Surface, surface2: pg.Surface):
    return surface1.get_view().raw == surface2.get_view().raw


class keyboard:
    pressed_keys = []
    clicks_pressed = []
    mouse_position = pg.Vector2(0, 0)
    true_mouse_position = pg.Vector2(0, 0)
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
        key = pg.key.name(key_number)
        keyboard.pressed_keys.append(key)

        if key in keyboard.key_map_execute_once.keys():

            function_to_execute: function = keyboard.key_map_execute_once[key][0]
            if len(keyboard.key_map_execute_once[key]) == 2:
                args = keyboard.key_map_execute_once[key][1]
                function_to_execute(*args)
            else:
                function_to_execute()

    def key_release(key):
        keyboard.pressed_keys.remove(pg.key.name(key))

    def is_key_pressed(key: str):
        return key in keyboard.pressed_keys

    def step():

        keyboard.mouse_position = pg.Vector2(
            pg.mouse.get_pos()[0] + camera.rect.x,
            pg.mouse.get_pos()[1] + camera.rect.y,
        )
        keyboard.true_mouse_position = pg.Vector2(
            pg.mouse.get_pos()[0],
            pg.mouse.get_pos()[1],
        )
        keyboard.clicks_pressed = pg.mouse.get_pressed(5)

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
        *args,
    ):
        if only_execute_function_one_time:
            keyboard.key_map_execute_once[key] = (function_to_execute_when_press,)
        else:
            keyboard.key_map_execute_on_step[key] = (function_to_execute_when_press,)


class Image:
    def __init__(self, path_or_surface: str | pg.Surface):
        if isinstance(path_or_surface, str):
            self.surface = pg.image.load(path_or_surface)
        else:
            self.surface = path_or_surface

        self.is_converted = False

    def convert(self):
        if not self.is_converted:
            self.surface = self.surface.convert_alpha()
            self.is_converted = True

    def scale(self, width: int, height: int):
        return pg.transform.scale(self.surface, (width, height))


class camera:
    rect: pg.Rect = None
    screen: pg.Surface = None
    movement = pg.Vector2((0, 0))

    def init():
        camera.rect = pg.display.get_surface().get_rect()

    def step():
        camera.apply_movement()

    def apply_movement():
        camera.rect.x += camera.movement.x
        camera.rect.y += camera.movement.y

    def show(
        image: pg.Surface | Image,
        position: pg.Rect | tuple[int, int],
        is_blocked_on_screen: bool = False,
    ):
        """if position is negative, it will be from the bottom or right of the screen"""
        if isinstance(position, tuple):
            position = image.get_rect(x=position[0], y=position[1])

        if isinstance(image, Image):
            image.convert()
            image = image.surface

        if position.x < 0:
            position.x += camera.rect.width
        if position.y < 0:
            position.y += camera.rect.height  # "+=" because it's negative number
        if is_blocked_on_screen:  # it's globally a pg.blit

            pg.display.get_surface().blit(image, position)
        else:
            relative_destination = pg.Rect(
                position.x - camera.rect.x,
                position.y - camera.rect.y,
                position.width,
                position.height,
            )

            if camera.rect.colliderect(
                position
            ):  # check if it's in the screen (optimization)
                pg.display.get_surface().blit(image, relative_destination)


class Visible_object:
    all_visible_objects: dict[int, list["Visible_object"]] = {}
    # format is depth:[list of all object with this depth]

    def init():
        max_depth = 255
        min_depth = 0
        for i in range(min_depth, max_depth):
            Visible_object.all_visible_objects[i] = []
        # initiatialising the dict so that it is ordered

    def step():
        for depth in Visible_object.all_visible_objects:
            for visible_object in Visible_object.all_visible_objects[depth]:
                camera.show(
                    visible_object.image,
                    visible_object.rect,
                    visible_object.is_fixed_to_the_screen,
                )

    def __init__(
        self,
        image: Image,
        rect_or_pos: pg.Rect | tuple[int, int],
        depth: int = 127,
        is_fixed_to_the_screen: bool = False,
        is_alive_at_start: bool = True,
    ):
        """depth: a higher depth will make the object be blitted at last, so will be on top of other surface, it goes from 0 to 255"""

        self.image = image
        if type(rect_or_pos) == pg.Rect:
            self.rect: pg.Rect = rect_or_pos
        else:
            self.rect = self.image.surface.get_rect(topleft=rect_or_pos)

        self.depth = depth
        self.is_alive = is_alive_at_start
        self.is_fixed_to_the_screen = is_fixed_to_the_screen

        Visible_object.all_visible_objects[self.depth].append(self)

    def show(self):
        self.is_alive = True

    def hide(self):
        self.is_alive = False

    def change_depth(self, new_depth: int):
        Visible_object.all_visible_objects[self.depth].remove(self)
        self.depth = new_depth
        Visible_object.all_visible_objects[self.depth].append(self)

    def set_xy(self, new_x: int, new_y: int):
        self.rect = self.rect.move(new_x, new_y)

    def change_image(self, new_image: Image):
        """please do not change image every tick, this function eat performance"""

        self.image = new_image
        self.rect = self.image.get_rect(topleft=self.rect.topleft)


class Button:
    all_buttons = []
    true_mouse_pos = (0, 0)

    def init():
        Button.true_mouse_pos = pg.mouse.get_pos()

    def __init__(
        self,
        image: Image,
        function_to_execute_on_click: "function",
        x: int = 0,
        y: int = 0,
        width: int = 100,
        height: int = 100,
        is_alive_at_start: bool = True,
        *args_to_function,
    ):
        self.x, self.y = x, y
        self.width, self.height = width, height

        self.image = image.scale(self.width, self.height)

        self.mask = pg.mask.from_surface(self.image, 1)
        self.rect = self.mask.get_rect(x=self.x, y=self.y)

        self.function = function_to_execute_on_click
        self.args = args_to_function

        keyboard.functions_to_execute_on_click.append((self.on_click))
        self.is_alive = is_alive_at_start
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

    pg.font.init()
    default_font = pg.font.Font(pg.font.get_default_font(), 20)

    def bar_percentage(
        percentage: float,
        width: int = 100,
        height: int = 25,
        bar_color: pg.Color = "white",
        background_color: pg.Color = None,
        border_size: int = 5,
        border_color: pg.Color | str = "black",
    ) -> pg.Surface:
        if border_size <= 0:
            raise ValueError("border size can't be less or equal to 0")

        output_surface = pg.Surface((width + border_size * 2, height + border_size * 2))
        if background_color != None:
            output_surface.fill(background_color)

        pg.draw.rect(
            output_surface,
            bar_color,
            pg.Rect(0, 0, width * percentage / 100, height),
        )

        pg.draw.rect(
            output_surface,
            border_color,
            output_surface.get_rect(),
            border_size,
        )

        return output_surface

    def text(text) -> pg.Surface:
        output_surface = draw.default_font.render(str(text), 1, "red")
        return output_surface


def step_to_all_module():
    keyboard.step()
    Button.step_all()
    camera.step()
    Visible_object.step()


def init_all_module():
    Visible_object.init()
    Button.init()
    camera.init()


def print_time_of_function(function, *args, **kwds):
    import time

    start_time = time.time()
    function(*args, **kwds)
    end_time = time.time()
    print("time took=", end_time - start_time)
