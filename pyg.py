import pygame as pg
import math, time, random
from typing import Union


def is_even(numb: int):
    return not numb & 1  # bitwise operation


def get_percentage(number: float, total: float):
    return number * 100 / total


def is_two_surfaces_equal(surface1: pg.Surface, surface2: pg.Surface):
    return surface1.get_view().raw == surface2.get_view().raw


def is_vectors_facing_same_direction(vector1: pg.Vector2, vector2: pg.Vector2):
    angle_between = vector1.angle_to(vector2)
    return -90 < angle_between < 90


def get_words(text: str) -> list[str]:
    """return a list of all of the words, seperated by space, it suppress all in the text"""
    words = []
    current_word = ""
    for letter in text:
        if letter == " ":
            words.append(current_word)
            current_word = ""
        else:
            current_word += letter
    words.append(current_word)  # for the last word
    return words


def convert_second(s: float, precision: int = 3):
    """return a string with the correct mesurement. The precision is the number of value after the coma (eg: convert s to ms)"""
    if s > 1:
        return str(round(s, precision)) + "s"
    elif s > 0.001:
        return str(round(s * (10**3), precision)) + "ms"
    else:
        return str(round(s * (10**6), precision)) + "μs"


def get_rect_info(rect: pg.Rect):
    """return the info to transform a rect into a tuple, and recover it in load_rect"""
    return rect.left, rect.top, rect.width, rect.height


def load_rect(info: tuple[int] | list[int]):
    """load a rect from the get_rect_info function"""
    rect = pg.Rect(*info)
    return rect


class Interval:
    def __init__(self, min: float, max: float):
        self.max = max
        self.min = min

    def __contains__(self, other: float):
        return self.min <= other and other <= self.max


class Cooldown:
    """generate a cooldown easely"""

    cooldowns_to_step: list["Cooldown"] = []

    def __init__(self, time: float):
        """
        Args:
            time (float): Time in second
        """
        self.tick_time = time * fps
        self.reset()

    def step(self):
        self.tick += 1
        if self.tick >= self.tick_time:
            self.destroy()

    @classmethod
    def step_all(cls):
        for cooldown in Cooldown.cooldowns_to_step:
            cooldown.step()

    def reset(self):
        Cooldown.cooldowns_to_step.append(self)
        self.tick = 0

    def destroy(self):
        if self in Cooldown.cooldowns_to_step:
            Cooldown.cooldowns_to_step.remove(self)

    def __bool__(self):
        return self.tick >= self.tick_time


class Profiler:
    """Count the time a certain function was used by using it as a decorator. Does not work if methods with the self arguments."""

    all_functions: dict["Profiler", list[int]] = {}
    precision = 3
    is_active = True
    ticks_number = 0

    def __init__(self, f):
        self.f = f
        if Profiler.is_active:
            Profiler.all_functions[self] = []

    def __call__(self, *args, **kwds):
        if not Profiler.is_active:
            return self.f(*args, **kwds)
        start_time = time.time()
        output = self.f(*args, **kwds)
        Profiler.all_functions[self].append(time.time() - start_time)
        return output

    @classmethod
    def step(cls):
        if Profiler.is_active:
            Profiler.ticks_number += 1

    @classmethod
    def on_end(cls):
        if not Profiler.is_active:
            return
        for profil in Profiler.all_functions.keys():
            time_values = Profiler.all_functions[profil]
            if time_values == []:
                continue

            number_of_calls = len(time_values)
            average_time_per_call = sum(time_values) / number_of_calls
            average_time_per_tick = average_time_per_call * (
                number_of_calls / Profiler.ticks_number
            )

            basic_info = f"""function: {profil.f.__qualname__ }: 
                average time per call: {convert_second(average_time_per_call)}
                calls :{number_of_calls}
                calcul time percentage (not accurate): {round((average_time_per_tick/dt) * 100)}%"""

            per_tick_info = f"""
                calls per tick: {number_of_calls/Profiler.ticks_number} 
                average time per tick: {convert_second(average_time_per_call*(number_of_calls/Profiler.ticks_number))}"""

            if number_of_calls / Profiler.ticks_number == 1:
                print(basic_info)
            else:
                print(basic_info + per_tick_info)


class keyboard:
    pressed_keys = []
    mouse_position = pg.Vector2(0, 0)
    true_mouse_position = pg.Vector2(0, 0)
    functions_to_execute_on_click = []
    click_map = {
        0: "left click",
        1: "middle click",
        2: "right click",
        3: "fourth click",  # the button on the side that's near the hand (fourth button)
        4: "fifth click",  # the button on the side that's far to the hand (fifth button)
    }

    clicks_pressed = (False, False, False, False, False)
    is_left_clicked_last_tick = False
    key_map_execute_on_step: dict[str, list[tuple["function", tuple]]] = {}
    key_map_execute_once: dict[str, list[tuple["function", tuple]]] = {}

    @classmethod
    def key_press(cls, key: int | str):
        if isinstance(key, int):
            key = pg.key.name(key)
        keyboard.pressed_keys.append(key)

        if key in keyboard.key_map_execute_once:

            for function_and_args in keyboard.key_map_execute_once[key]:
                function, args = function_and_args
                if args != None:
                    function(*args)
                else:
                    function()

    @classmethod
    def key_release(cls, key: int | str):
        if isinstance(key, int):
            key = pg.key.name(key)

        keyboard.pressed_keys.remove(key)

    @classmethod
    def is_key_pressed(cls, key: str):
        return key in keyboard.pressed_keys

    @classmethod
    def step(cls):
        keyboard.mouse_position = pg.Vector2(
            pg.mouse.get_pos()[0] + camera.rect.x,
            pg.mouse.get_pos()[1] + camera.rect.y,
        )
        keyboard.true_mouse_position = pg.Vector2(pg.mouse.get_pos())

        keyboard.update_mouse_click()
        keyboard.clicks_pressed = pg.mouse.get_pressed(5)

        keyboard.execute_on_click.execute_all_function_on_click()
        keyboard.execute_key_map_on_step()

        keyboard.is_left_clicked_last_tick = (
            keyboard.click_map[0] in keyboard.pressed_keys
        )

    @classmethod
    def update_mouse_click(cls):
        """this function update the keyboard.pressed_keys with the pressed clicks"""
        for click_currently_checking in range(5):
            if keyboard.clicks_pressed[click_currently_checking]:
                if (
                    keyboard.click_map[click_currently_checking]
                    not in keyboard.pressed_keys
                ):
                    keyboard.key_press(keyboard.click_map[click_currently_checking])

            elif keyboard.click_map[click_currently_checking] in keyboard.pressed_keys:
                keyboard.key_release(keyboard.click_map[click_currently_checking])

    class execute_on_click:
        """execute automaticly the function when the left mouse button is clicked, it can't take argument nor output the result of the function"""

        def __init__(self, function, *args):
            if function not in keyboard.functions_to_execute_on_click:
                keyboard.functions_to_execute_on_click.append((function, args))

        def __call__(self, function, *args, **kwds):
            function(*args, **kwds)

        @classmethod
        def execute_all_function_on_click(cls):
            if (
                keyboard.click_map[0] in keyboard.pressed_keys
                and not keyboard.is_left_clicked_last_tick
            ):  # if left button is pressed
                for function_and_args in keyboard.functions_to_execute_on_click:
                    function = function_and_args[0]
                    args = function_and_args[1]
                    if args != None:
                        function(*args)
                    else:
                        function()

    @classmethod
    def mouse_wheel_scroll(cls, event: pg.event.Event):
        is_up_scroll = event.y == 1
        keyboard.on_mouswheel_scroll.call_all(is_up_scroll)

    class on_mouswheel_scroll:
        up_function_and_args: list["function", list] = []
        down_function_and_args: list["function", list] = []

        def __init__(self, function: "function", is_up_scroll: bool, *args):
            if is_up_scroll:
                keyboard.on_mouswheel_scroll.up_function_and_args.append(
                    (function, args)
                )
            else:
                keyboard.on_mouswheel_scroll.down_function_and_args.append(
                    (function, args)
                )

        def __call__(self, function, *args, **kwds):
            function(*args, **kwds)

        @classmethod
        def call_all(cls, up_scroll: bool):
            if up_scroll:
                for (
                    function_and_args
                ) in keyboard.on_mouswheel_scroll.up_function_and_args:
                    function = function_and_args[0]
                    args = function_and_args[1]
                    if args == None:
                        function()
                    else:
                        function(*args)
            else:
                for (
                    function_and_args
                ) in keyboard.on_mouswheel_scroll.down_function_and_args:
                    function = function_and_args[0]
                    args = function_and_args[1]
                    if args == None:
                        function()
                    else:
                        function(*args)

    @classmethod
    def set_new_key_map(
        cls,
        keys: str | list[str],
        execute_function_once: bool,
        function: "function",
        *args_for_function,
    ):
        """Add a function which will be executed on key

        Args:
            keys (str | list[str]): when is a list, function is executed for any of the key provided
            only_execute_function_one_time (bool): execute function once on key press or continuously when key is pressed
        """
        if isinstance(keys, str):
            keys = [keys]
        for key in keys:
            if execute_function_once:
                key_list = keyboard.key_map_execute_once.get(key, [])
                # .get because the dict isn't initialised with an empty list at each key, then, i reassing it
                key_list.append((function, args_for_function))
                keyboard.key_map_execute_once[key] = key_list
            else:
                key_list = keyboard.key_map_execute_on_step.get(key, [])
                # .get because the dict isn't initialised with an empty list at each key, then, i reassing it
                key_list.append((function, args_for_function))
                keyboard.key_map_execute_on_step[key] = key_list

    @classmethod
    def execute_key_map_on_step(cls):
        for key in keyboard.key_map_execute_on_step:
            if keyboard.is_key_pressed(key):
                for function_and_args in keyboard.key_map_execute_on_step[key]:
                    function = function_and_args[0]
                    args = function_and_args[1]
                    if args != None:
                        function(*args)
                    else:
                        function()

    @classmethod
    def is_mod_active(cls, mod_to_check: int):
        """return if mod is pressed (eg: shift, alt..), enter the mod_to_check with pg.KMOD_..."""
        mods = pg.key.get_mods()
        return mods & mod_to_check


class camera:
    movement = pg.Vector2((0, 0))

    @classmethod
    def init(cls, max_depth=255):
        camera.screen = pg.display.get_surface()
        camera.rect = camera.screen.get_rect()
        camera.max_depth = max_depth
        camera.reset_depths()

    @classmethod
    def reset_depths(cls):
        camera.all_images: list[list[tuple[pg.Surface, tuple[int, int], int]]] = []
        for _ in range(camera.max_depth + 1):
            camera.all_images.append([])

    @Profiler
    @staticmethod
    def draw_all_image():
        for depth_layer in camera.all_images:
            if depth_layer == []:
                continue
            for i, (
                surface,
                position,
                is_blocked_on_screen,
                special_flags,
            ) in enumerate(depth_layer):

                if not is_blocked_on_screen:
                    depth_layer[i] = (
                        surface,
                        (position[0] - camera.rect.x, position[1] - camera.rect.y),
                        None,
                        special_flags,
                    )
                else:
                    depth_layer[i] = surface, position, None, special_flags
            camera.screen.blits(depth_layer)

    def __init__(
        self,
        surface: pg.Surface,
        position: tuple[int, int],
        depth: int = -100,
        is_blocked_on_screen: bool = False,
        is_position_the_center: bool = False,
        special_flags: int = 0,
    ):
        """For rendering image on screen, all included.

        Args:
            position (tuple[int, int]): the relative or not position (depends on the arg "is_blocked_on_screen")
            depth (int): A higher depth make the images on top, the depth.
            A negative value will make it start from the end (eg: passing -1 is the same as passing max_depth-1).
            The max depth is defined in the class init.
            is_blocked_on_screen (bool, optional): is following the camera movement, recommended to enable for UI.
            is_position_the_center (bool, optional):  is the position the center of the image or the top left
        """

        if depth < 0:
            depth = camera.max_depth + depth  # + because it's negative

        depth = round(depth)
        depth = pg.math.clamp(depth, -camera.max_depth, camera.max_depth)

        if is_position_the_center:
            position = (
                position[0] - surface.get_width() / 2,
                position[1] - surface.get_height() / 2,
            )

        if not isinstance(surface, pg.Surface):
            raise ValueError(
                f"The surface argument must be a surface, not {type(surface)}"
            )

        camera.all_images[depth].append(
            (surface, position, is_blocked_on_screen, special_flags)
        )

    @classmethod
    def step(cls):
        camera.apply_movement()
        Camera_effect.step_all()
        camera.draw_all_image()
        camera.reset_depths()

    @classmethod
    def follow_position(cls, pos: tuple[int, int], weight: float):
        """make the camera follow a certain position in his center

        Args:
            pos (tuple[int,int]): center position
            weight (float): a float between 0 and 1, it's a linear interpolation
        """
        camera.rect.center = (
            pg.math.lerp(camera.rect.centerx, pos[0], weight),
            pg.math.lerp(camera.rect.centery, pos[1], weight),
        )

    @classmethod
    def apply_movement(cls):
        camera.rect.x += camera.movement.x
        camera.rect.y += camera.movement.y
        camera.movement = pg.Vector2(0, 0)


class Animated_sprite:
    """create a gif like sprite"""

    def __init__(self, surfaces: list[pg.Surface], time_between_frames: float = 0.15):
        self.surfaces = surfaces
        self.tick = 0
        self.tick_between_frames = round(time_between_frames * fps)

    def render(self):
        """Return the actual surface and change the index by one"""
        surface = self.surfaces[self.tick // self.tick_between_frames]
        self.tick += 1
        if len(self.surfaces) * self.tick_between_frames <= self.tick:
            self.tick = 0
        return surface

    def get_surface(self):
        """Return the actual surface, without changing the index by one"""
        return self.surfaces[self.tick]


class Camera_effect:
    all_active_effect: list["Camera_effect"] = []

    def __init__(self):
        Camera_effect.all_active_effect.append(self)

    def destroy(self):
        Camera_effect.all_active_effect.remove(self)

    def step(self):
        """A method for subclass, will be called each frame"""
        pass

    @classmethod
    def step_all(cls):
        for camera_effect in Camera_effect.all_active_effect:
            camera_effect.step()


class Screen_shake(Camera_effect):
    def __init__(self, intensity: int = 1, duration: float = 1):

        super().__init__()
        self.shake_vector: pg.Vector2 = pg.Vector2(0, 0)

        self.tick_lifetime = duration * fps
        """The number of tick the shake effect will last"""
        self.intensity = intensity
        self.ticks_elapsed = 0

    def step(self):
        self.ticks_elapsed += 1
        if self.ticks_elapsed >= self.tick_lifetime:
            self.destroy()
            return
        self.shake_vector = pg.Vector2(
            self.shake_vector[0] + random.uniform(-self.intensity, self.intensity),
            self.shake_vector[1] + random.uniform(-self.intensity, self.intensity),
        )
        self.shake_vector.clamp_magnitude_ip(0, self.tick_lifetime / self.ticks_elapsed)
        camera.movement += self.shake_vector


class draw:
    """class to get special surface easily"""

    pg.font.init()
    default_font = pg.font.Font(pg.font.get_default_font(), 20)

    @classmethod
    def bar_percentage(
        cls,
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

    @staticmethod
    def text(
        text: str,
        font_color: pg.Color = "black",
        font: pg.font.Font = default_font,
        rect_to_write_on: pg.Rect = None,
    ) -> pg.Surface:
        """text renderer, auto-wrap word if the rect_to_write_on argument is passed,
        Args:
            rect_to_write_on: the maximum size allowed for the text
        """
        if rect_to_write_on == None:
            output_surface = font.render(str(text), True, font_color)
        else:
            output_surface = pg.Surface(rect_to_write_on.size, pg.SRCALPHA)

            width = rect_to_write_on.width

            lines: list[str] = []
            current_line = ""

            words = get_words(text)

            for word in words:
                if (
                    font.size(current_line)[0] >= width
                    or font.size(current_line)[0] + font.size(word)[0] >= width
                ):
                    lines.append(current_line)
                    current_line = ""

                current_line += word + " "

            lines.append(current_line)

            if len(lines) * font.get_height() > rect_to_write_on.height:
                raise ValueError(
                    f'The rect ({rect_to_write_on}) passed isn\'t big enough to render the text "{text}"'
                )

            for i, line in enumerate(lines):
                text_surface = font.render(line, True, font_color, None)
                output_surface.blit(text_surface, (0, i * (font.get_height())))
        return output_surface

    @staticmethod
    def rect(rect: pg.Rect, color="green", border_size: int = 5):
        """Draw a rectangle on a new surface, it is mainly useful for debugging, it is not really optimized"""
        rect_surface = pg.Surface(rect.size, flags=pg.SRCALPHA)
        rect_surface.fill((0, 0, 0, 0))
        rect_at_00 = rect.copy()
        rect_at_00.topleft = (0, 0)
        pg.draw.rect(rect_surface, color, rect_at_00, border_size)
        return rect_surface

    @classmethod
    def fps_counter(cls):
        text_surface: pg.Surface = draw.default_font.render(
            str(round(clock.get_fps())),
            True,
            "red",
            "black",
        )
        return text_surface


class Collision_object:
    all_collision_object: list["Collision_object"] = []
    lasting_forces: list[tuple[pg.Vector2, int, int, bool]] = []
    debug_mode = False
    is_init = False

    @classmethod
    def init(cls, start_pos: tuple[int, int], collision: pg.Surface | pg.Rect):
        """init the class to start checking for collision with the player who interacts with collision object

        Args:
            start_pos (tuple[int, int]): The starting position of the player
            collision (pg.Surface| pg.Rect,): the collision to check, only the rectangle of the surface will be used if a surface is passed
        """

        if isinstance(collision, pg.Surface):
            Collision_object.player_rect = collision.get_bounding_rect()
        else:
            Collision_object.player_rect = collision.copy()
        Collision_object.player_rect.topleft = start_pos

        Collision_object.player_movement = pg.Vector2(0, 0)
        Collision_object.is_init = True

    @staticmethod
    def get_xy_of_player(is_pos_center: bool = False):
        """return topleft or center position of the player,"""
        if is_pos_center:
            return Collision_object.player_rect.center

        else:
            return Collision_object.player_rect.topleft

    @classmethod
    def set_xy_of_player(cls, pos: tuple[int, int]):
        Collision_object.player_rect.topleft = pos

    @classmethod
    def add_force_on_player(cls, force: pg.Vector2):
        """apply an instant movement for one tick to the player"""
        Collision_object.player_movement += force

    @classmethod
    def add_lasting_force_on_player(
        cls,
        force: pg.Vector2,
        duration_second: float = 1,
        is_sinus_decelerate: bool = False,
    ):
        """apply a force to the player that will last for the duration(in second)"""
        Collision_object.lasting_forces.append(
            (force, round(duration_second * fps), 0, is_sinus_decelerate)
        )

    @classmethod
    def step_lasting_forces(cls):
        for i, (vector, max_duration, duration, is_sinus) in enumerate(
            Collision_object.lasting_forces
        ):
            duration += 1
            if duration >= max_duration:
                Collision_object.lasting_forces.pop(i)
            else:
                Collision_object.lasting_forces[i] = (
                    vector,
                    max_duration,
                    duration,
                    is_sinus,
                )
            if is_sinus:
                percent_of_vector = math.asin(duration / max_duration) / (math.pi / 2)
            else:
                percent_of_vector = duration / max_duration

            vector = vector.copy()
            vector.lerp((0, 0), percent_of_vector)
            Collision_object.add_force_on_player(vector)

    def __init__(
        self,
        pos: tuple[int, int],
        collision: pg.Surface | pg.Rect,
        is_pos_center: bool = False,
    ):
        """generate a new object which will interact with the player (eg: a wall, floor..)

        Args:
            pos (tuple[int, int]): The position of the object, it could be the top left corner or the center
            collision (pg.Surface| pg.Rect,): the collision to add
            is_pos_center (bool, optional): if the position is the top left corner or the center. Defaults to False.
        """

        Collision_object.all_collision_object.append(self)
        if isinstance(collision, pg.Surface):
            self.rect = collision.get_bounding_rect()
            """The collision rect, it can be smaller than the global rect"""
            self.global_rect = collision.get_rect()
            """The rect that handle the position, it can be bigger than the collision rect"""
        else:
            self.rect = collision.copy()
            self.global_rect = collision.copy()

        if is_pos_center:
            self.global_rect.center = pos
        else:
            self.global_rect.topleft = pos
        self.rect.move_ip(self.global_rect.topleft)

    def destroy(self):
        Collision_object.all_collision_object.remove(self)

    @classmethod
    def step_all(cls):
        Collision_object.step_lasting_forces()
        if Collision_object.debug_mode:
            Collision_object.step_debug_mode()

        Collision_object.player_rect.move_ip(
            Collision_object.player_movement.x, 0
        )  # I first check if the x collides, then the y, idk if i can do something else
        colliding_object = Collision_object.get_colliding_object()
        if colliding_object != None:
            if Collision_object.player_movement.x > 0:
                Collision_object.player_rect.right = colliding_object.rect.left
            else:
                Collision_object.player_rect.left = colliding_object.rect.right

        Collision_object.player_rect.move_ip(0, Collision_object.player_movement.y)
        colliding_object = Collision_object.get_colliding_object()
        if colliding_object != None:
            if Collision_object.player_movement.y < 0:
                Collision_object.player_rect.top = colliding_object.rect.bottom
            else:
                Collision_object.player_rect.bottom = colliding_object.rect.top

        Collision_object.player_movement = pg.Vector2(0, 0)

    @classmethod
    def get_colliding_object(cls):
        """Return the first Collision object colliding with the player, return None if there isn't any"""
        colliding_object_index = Collision_object.player_rect.collidelist(
            Collision_object.all_collision_object
        )
        if colliding_object_index != -1:
            return Collision_object.all_collision_object[colliding_object_index]

    @classmethod
    def enable_debug_mode(cls):
        """Will show the rect of the player in green, and of the collisions object in blue"""
        Collision_object.debug_mode = True

    @classmethod
    def step_debug_mode(cls):
        for collision_object in Collision_object.all_collision_object:
            camera(
                draw.rect(collision_object.rect, "blue", 1),
                collision_object.rect.topleft,
                -2,
            )
        camera(
            draw.rect(Collision_object.player_rect, "red", 1),
            Collision_object.player_rect.topleft,
            -2,
        )


class Button:
    all_buttons: list["Button"] = []
    true_mouse_pos = (0, 0)

    @classmethod
    def init(cls):
        Button.true_mouse_pos = pg.mouse.get_pos()

    def __init__(
        self,
        surface: pg.Surface,
        left_click_function: "function",
        pos_or_rect: tuple[int, int] | pg.Rect,
        args_to_lmb_function: tuple = (),
        is_alive_at_start: bool = True,
        right_click_function: "function" = None,
        right_click_function_args: tuple = None,
    ):
        if isinstance(pos_or_rect, pg.Rect):
            self.rect = pos_or_rect
            self.surface = pg.transform.scale(surface, self.rect.size)
        else:
            self.rect = surface.get_rect(topleft=pos_or_rect)
            self.surface = surface

        self.mask = pg.mask.from_surface(self.surface, 1)

        self.lmb_function = left_click_function
        if isinstance(args_to_lmb_function, tuple):
            self.lmb_args = args_to_lmb_function
        else:
            self.lmb_args = (args_to_lmb_function,)

        self.rmb_function = right_click_function
        if isinstance(right_click_function_args, tuple):
            self.rmb_args = right_click_function_args
        else:
            self.rmb_args = (right_click_function_args,)
        keyboard.execute_on_click(self.on_click, False)
        if self.rmb_function != None:
            keyboard.set_new_key_map(
                "right click",
                True,
                self.on_click,
                True,
            )

        self.is_visible = is_alive_at_start
        Button.all_buttons.append(self)

    def destroy(self):
        Button.all_buttons.remove(self)

    def step(self):
        if self.is_visible:
            self.draw()

    def set_surface(self, surface: pg.Surface):
        self.surface = pg.transform.scale(surface, self.rect.size)
        self.mask = pg.mask.from_surface(self.surface)

    def draw(self):
        camera(self.surface, self.rect, -52, True)

    @classmethod
    def step_all(cls):
        for button in Button.all_buttons:
            button.step()

    def on_click(self, is_rmb: bool):
        """
        Args:
            is_rmb (bool): determine if it's the left or right click
        """
        if (
            self.is_visible
            and self.rect.collidepoint(*keyboard.true_mouse_position.xy)
            and self.mask.get_at(
                (
                    keyboard.true_mouse_position.x - self.rect.x,
                    keyboard.true_mouse_position.y - self.rect.y,
                )
            )
        ):
            if not is_rmb:
                if self.lmb_args == None:
                    self.lmb_function()
                else:
                    self.lmb_function(*self.lmb_args)
            elif self.rmb_function is not None:
                if self.rmb_args == None:
                    self.rmb_function()
                else:
                    self.rmb_function(*self.rmb_args)

    @staticmethod
    def is_position_in_zone_covered(
        x: int, y: int, is_position_relative: bool = True
    ) -> bool:
        if is_position_relative:
            x = x - camera.rect.x
            y = y - camera.rect.y
        for button in Button.all_buttons:
            if (
                button.is_visible
                and button.rect.collidepoint((x, y))
                and button.mask.get_at(
                    (
                        x - button.rect.x,
                        y - button.rect.y,
                    )
                )
            ):  # if clicked the button (the rect checking is just for optimization)
                return True
        return False

    def __str__(self):
        return f"Button: lmb_function:{self.lmb_function}{self.lmb_args}, rmb_function: {self.rmb_function}{self.rmb_args}"

    def __repr__(self):
        return self.__str__()


class Explain_bubble:
    alls: list["Explain_bubble"] = []
    old_mouse_pos = (0, 0)
    same_pos_tick = 0
    """the number of tick the mouse stayed on the same position"""
    hovering_time = 20
    """the number of tick the mouse has to stay on the same position to display an explanation"""

    def __init__(self, object_rect: pg.Rect, surface: pg.Surface):
        """_summary_

        Args:
            object_rect (pg.Rect): The rect of the object when hovered will display the explanation,
            it has to be a fixed rect and not relative to the camera
            surface (pg.Surface): The explanation
        """
        self.rect = object_rect
        self.surface = surface
        Explain_bubble.alls.append(self)
        self.is_visible = False

    @classmethod
    def step_all(cls):
        if Explain_bubble.same_pos_tick >= Explain_bubble.hovering_time:
            hovering_explanation = Explain_bubble.get_hovering_explanation()
            if hovering_explanation != None and hovering_explanation.is_visible:
                camera(
                    hovering_explanation.surface,
                    keyboard.true_mouse_position,
                    -50,
                    True,
                    False,
                )

        if Explain_bubble.old_mouse_pos == keyboard.true_mouse_position:
            Explain_bubble.same_pos_tick += 1
        else:
            Explain_bubble.same_pos_tick = 0
        Explain_bubble.old_mouse_pos = keyboard.true_mouse_position

    @staticmethod
    def get_hovering_explanation() -> Union["Explain_bubble", None]:
        # I use union 'cause one of them is a string and python don't like that
        index = pg.Rect.collidelist(
            pg.Rect(
                keyboard.true_mouse_position, (1, 1)
            ),  # the mini rect is the mouse pos
            Explain_bubble.alls,
        )
        if index != -1:
            return Explain_bubble.alls[index]
        else:
            return None

    def toggle_visibility(self, state: bool = None):
        """_summary_

        Args:
            state (bool): toggle the visibility state(None) or show(True) or hide(False). Defaults to None.
        """
        if state is None:
            self.is_visible = not self.is_visible
        else:
            self.is_visible = state

    def __str__(self):
        return "Explanation_object:" + str(self.rect)


def shutdown():
    if function_to_call_on_shutdown is not None:
        function_to_call_on_shutdown()
    Profiler.on_end()
    pg.quit()
    exit()


@Profiler
def step_to_all_module():
    for event in pg.event.get():
        if event.type == pg.QUIT:
            shutdown()

        elif event.type == pg.KEYDOWN:
            keyboard.key_press(event.key)
        elif event.type == pg.KEYUP:
            keyboard.key_release(event.key)

        elif event.type == pg.MOUSEWHEEL:
            keyboard.mouse_wheel_scroll(event)

    keyboard.step()
    Button.step_all()
    camera.step()
    Profiler.step()
    Explain_bubble.step_all()
    Cooldown.step_all()

    if Collision_object.is_init:
        Collision_object.step_all()

    global dt
    dt = clock.tick_busy_loop(fps) / 1000


def init_all_module(
    fps_: int,
    is_profiler_active: bool = False,
    function_to_call_on_shutdown_: "function" = None,
):
    global function_to_call_on_shutdown
    function_to_call_on_shutdown = function_to_call_on_shutdown_

    global fps, clock, dt
    fps = fps_
    dt = 1 / fps
    clock = pg.time.Clock()

    Button.init()
    camera.init(2000)

    Profiler.is_active = is_profiler_active
