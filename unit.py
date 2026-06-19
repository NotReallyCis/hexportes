from pyg import camera, draw, get_percentage
import pygame as pg
import data, pyg, abc, random
from typing import Type

from typing import TYPE_CHECKING

if TYPE_CHECKING:  # resolve the circular import type hinting issue
    from hex import Hex
else:

    class Hex:  # empty class replaced with the Hex just below
        pass


def get_variable(variable, default):
    """return The variable if it's not none and the default otherwise (similar to git.dict)"""
    if variable is None:
        return default
    else:
        return variable


class Bar:
    height = 5
    width = 50

    def __init__(self, color: pg.Color, max_value: int, value: int = None):
        self.color = color
        self.max_value = max_value
        self.value = get_variable(value, max_value)

    @property
    def value(self):
        return self._value

    @value.setter
    def value(self, new_value: int):
        self._value = new_value
        self.surface = self.get_surface()

    def get_surface(self):
        surface = draw.bar_percentage(
            get_percentage(self.value, self.max_value),
            self.width,
            self.height,
            self.color,
            border_size=1,
        )
        return surface

    def draw(self, pos):
        camera(self.surface, pos)


class Component(abc.ABC):
    """Base class for all components"""

    def __init__(self, unit: Unit, info: dict[str]):
        self.unit = unit
        self.unit.components[self.get_name()] = self

    def step(self):
        """called each tick"""
        pass

    def unit_selected(self):
        pass

    def unit_unselected(self):
        pass

    def on_click(self, clicked_hex: Hex):
        pass

    def get_info(self) -> dict[str]:
        return {}

    @classmethod
    def get_name(cls):
        return cls.__name__

    def add_bar(self, bar: Bar):
        self.unit.bars.append(bar)

    def after_movemement(self):
        pass

    def __str__(self):
        return self.get_name()


class Component_movement(Component):
    FUEL = "fuel"
    MAX_FUEL = "max fuel"
    MOVEMENT_POINT = "movement point"

    def __init__(self, unit, info):
        super().__init__(unit, info)
        self.movement_point = self.default_movement_point = unit.get_type_info()[
            Component_movement.MOVEMENT_POINT
        ]
        self.max_fuel = unit.get_type_info()[self.MAX_FUEL]
        self.fuel = info.get(Component_movement.FUEL, self.max_fuel)
        self.fuel_bar = Bar("brown", self.max_fuel, self.fuel)
        self.add_bar(self.fuel_bar)
        self.unit.add_button(data.go_button, Component_movement.switch_state)
        self.reset_possible_hexs_to_go()

    def get_info(self):
        return {
            Component_movement.MOVEMENT_POINT: self.default_movement_point,
            Component_movement.FUEL: self.fuel,
        }

    CHOOSE_DESTINATION_STATE = "choose destination"

    @staticmethod
    def switch_state():
        data.current_state = Component_movement.CHOOSE_DESTINATION_STATE

    def on_click(self, hex: Hex):
        if (
            data.current_state != Component_movement.CHOOSE_DESTINATION_STATE
            or not self.unit.is_selected
        ):
            return
        if hex.unit_on_hex is not None or hex not in self.possible_hexs_to_go:
            self.unit.unselect()
            return
        fuel_after_movement = self.fuel - (
            self.movement_point - self.possible_hexs_to_go[hex]
        )
        if fuel_after_movement < 0:
            self.unit.unselect()
            return

        self.fuel = fuel_after_movement
        self.fuel_bar.value = self.fuel
        self.movement_point = self.possible_hexs_to_go[hex]
        self.unit.move_to(hex)

        return super().on_click(hex)

    def reset_possible_hexs_to_go(self):
        self.possible_hexs_to_go = (
            self.unit.get_hex().search_hex(self.movement_point, True).copy()
        )

    def after_movemement(self):
        self.reset_possible_hexs_to_go()
        return super().after_movemement()

    def step(self):
        if (
            data.current_state == Component_movement.CHOOSE_DESTINATION_STATE
            and self.unit.is_selected
        ):
            for possible_hex_to_go in self.possible_hexs_to_go:
                possible_hex_to_go.draw_surface_on_top(data.hex_can_go)

        return super().step()


class Component_vision(Component):
    VIEW_RANGE = "view range"

    def __init__(self, unit, info):
        super().__init__(unit, info)
        self.view_range = unit.get_type_info()[Component_vision.VIEW_RANGE]
        self.calculate_vision()

    def calculate_vision(self):
        if self.unit.team is not self.unit.team_of_main:
            return
        visible_hexs = self.unit.get_hex().search_hex(self.view_range, False)
        for hex in visible_hexs:
            hex.remove_fog()

    def after_movemement(self):
        self.calculate_vision()
        return super().after_movemement()


class Component_attack(Component):
    DAMAGE = "damage"
    AMMO = "ammo"
    MAX_AMMO = "max ammo"
    RANGE = "range"
    attack_button = data.attack_button
    ATTACK_STATE = "attack"
    hex_can_attack = data.hex_can_attack
    attackable_hexs: list[Hex]

    def __init__(self, unit, info: dict[str]):
        super().__init__(unit, info)
        self.damage = int(unit.get_type_info()[self.DAMAGE])
        max_ammo = unit.get_type_info()[self.MAX_AMMO]
        self.ammo = info.get(self.AMMO, max_ammo)
        self.attack_range = unit.get_type_info()[self.RANGE]

        self.add_bar(Bar("red", max_ammo, self.ammo))
        self.unit.add_button(
            Component_attack.attack_button, Component_attack.switch_attack_mode
        )
        self.reset_attackable_hexs()

    @staticmethod
    def switch_attack_mode():
        data.current_state = Component_attack.ATTACK_STATE

    def on_click(self, hex):
        if data.current_state == Component_attack.ATTACK_STATE:
            self.attack_tile(hex)
        return super().on_click(hex)

    def attack_tile(self, hex: Hex):
        unit = hex.unit_on_hex
        if (
            (unit is None)
            or (unit.team == self.unit.team)
            or (not unit.has_component(Component_attack))
        ):
            return
        pv_component: Component_pv = unit.get_component(Component_pv)
        pv_component.damage(self.damage)

    def after_movemement(self):
        self.reset_attackable_hexs()
        return super().after_movemement()

    def step(self):
        if data.current_state == Component_attack.ATTACK_STATE:
            self.draw_attackable_hexs()
        return super().step()

    def reset_attackable_hexs(self):
        self.attackable_hexs = self.unit.get_hex().search_hex(self.attack_range, False)

    def draw_attackable_hexs(self):
        for hex in self.attackable_hexs:
            hex.draw_surface_on_top(Component_attack.hex_can_attack)


class Component_pv(Component):
    PV = "pv"
    MAX_PV = "max pv"

    def __init__(self, unit, info):
        super().__init__(unit, info)
        max_pv = unit.get_type_info()[Component_pv.MAX_PV]
        self.pv = int(info.get(Component_pv.PV, max_pv))
        self.pv_bar = Bar("green", max_pv, self.pv)
        self.add_bar(self.pv_bar)

    def get_info(self):
        return {Component_pv.PV: self.pv}

    def damage(self, amount: int):
        self.pv -= amount
        self.pv_bar.value = self.pv
        if self.pv <= 0:
            self.unit.destroy()


IMAGE = "image"
COMPONENTS = "components"

TEST_UNIT = "first_test"

unit_type = {
    TEST_UNIT: {
        IMAGE: "tile-village.png",
        COMPONENTS: [
            Component_pv,
            Component_movement,
            Component_attack,
            Component_vision,
        ],
        Component_movement.MOVEMENT_POINT: 4,
        Component_movement.MAX_FUEL: 10,
        Component_vision.VIEW_RANGE: 5,
        Component_pv.MAX_PV: 10,
        Component_attack.DAMAGE: 5,
        Component_attack.MAX_AMMO: 20,
        Component_attack.RANGE: 5,
    },
}


def get_unit_image_by_unit_and_color(unit_name: str, color: str):
    image_name = unit_type[unit_name][IMAGE]
    return pg.image.load(data.directory_unit_team_color + color + "_" + image_name)


class Unit:
    all_units: list[Unit] = []
    unit_selected: None | Unit = None

    color_remaining = data.all_colors
    selected_bad_unit_sound = data.selected_bad_unit_sound

    button_size = pg.Rect(0, 0, 50, 50)

    @classmethod
    def init(cls, team: int):
        """create a new team"""
        Unit.team_of_main = team

        Unit.map_teams_to_color = {Unit.team_of_main: Unit.color_remaining[0]}
        Unit.color_remaining.pop(0)

    def add_component(self, component: type[Component], info: dict[str]):
        component(self, info)

    def has_component(self, component: Type[Component] | str):
        if not isinstance(component, str):
            component = component.get_name()
        return component in self.components

    def get_component(self, component: Type[Component] | str):
        if not isinstance(component, str):
            component = component.get_name()
        return self.components[component]

    @classmethod
    def from_name(cls, w: int, h: int, name: str, team: int):
        return Unit(w, h, {Unit.TEAM: team, Unit.NAME: name})

    def __init__(
        self,
        w: int,
        h: int,
        info: dict[str],
    ):
        self.w = w
        self.h = h

        self.id = random.random()
        self.name = info[Unit.NAME]
        self.team = info[Unit.TEAM]
        self.set_color()
        self.set_image()

        if self.get_hex().unit_on_hex != None:
            raise ValueError(
                f"hex({w,h}) is arleady taken by another unit, can't generate here"
            )
        self.get_hex().unit_on_hex = self

        self.is_selected = False

        self.components: dict[str, Component] = {}
        self.bars: list[Bar] = []
        self.all_buttons: list[pyg.Button] = []
        Unit.all_units.append(self)
        for component in unit_type[self.name][COMPONENTS]:
            self.add_component(component, info)

    TEAM = "team"
    NAME = "name"

    def get_info(self):
        """return a dict with all the informations to create a new unit"""
        info = {Unit.TEAM: self.team, Unit.NAME: self.name}
        for component in self.components.values():
            info = info | component.get_info()
        return info

    def get_type_info(self):
        return unit_type[self.name]

    def set_image(self):
        self.image = get_unit_image_by_unit_and_color(self.name, self.color)

    def set_color(self):
        if self.team in Unit.map_teams_to_color.keys():
            self.color = Unit.map_teams_to_color[self.team]
        else:
            Unit.map_teams_to_color[self.team] = Unit.color_remaining[0]
            Unit.color_remaining.pop(0)
            self.color = Unit.map_teams_to_color[self.team]

    def destroy(self):
        if self.is_selected:
            self.unselect()
        self.get_hex().unit_on_hex = None
        Unit.all_units.remove(self)

    @classmethod
    def destroy_all_units(cls):
        for unit in Unit.all_units:
            unit.destroy()
        Unit.all_units = []

    def __str__(self):
        return str((self.name, self.team, self.id))

    def __repr__(self):
        return self.__str__()

    def step(self):
        for component in self.components.values():
            component.step()

        if self.get_hex().is_visible:
            self.draw()
            self.draw_info()

    @classmethod
    def step_all_units(cls):
        for unit in Unit.all_units:
            unit.step()

    def draw(self):
        from hex import Hex

        x, y = Hex.get_xy_by_wh(self.w, self.h)
        camera(self.image, (x, y))

    def draw_info(self):
        x, y = self.get_xy()
        for i, bar in enumerate(self.bars):
            bar.draw((x, y - (i * Bar.height)))

    def add_button(self, surface: pg.Surface, function: "function"):
        rect = Unit.button_size.copy()
        rect.x = (
            len(self.all_buttons) + 1
        ) * Unit.button_size.width  # +1 for the pass turn button
        button = pyg.Button(surface, function, rect)
        button.is_visible = False
        self.all_buttons.append(button)

    def get_hex(self):
        """Get the hex where the unit is"""
        from hex import Hex

        return Hex.get_hex_by_wh(self.w, self.h)

    def get_xy(self):
        return (self.get_hex().x, self.get_hex().y)

    def select(self):
        if self.is_selected:
            raise ValueError(
                f"you can't select a unit that is arleady selected, (unit selected:{ self.__str__()})",
            )

        if self.team != Unit.team_of_main:
            Unit.selected_bad_unit_sound.play()
            return

        for button in self.all_buttons:
            button.is_visible = True

        self.is_selected = True
        Unit.unit_selected = self
        for component in self.components.values():
            component.unit_selected()
        if self.has_component(Component_movement):
            data.current_state = Component_movement.CHOOSE_DESTINATION_STATE

    def unselect(self):
        if not self.is_selected:
            raise ValueError(
                f"you can't unselect a unit that is not selected, (unit unselected:{self.__str__()})",
            )

        self.is_selected = False
        Unit.unit_selected = None
        for component in self.components.values():
            component.unit_unselected()

        for button in self.all_buttons:
            button.is_visible = False
        data.current_state = data.click_state.SELECT_UNIT

    def on_click(self, clicked_hex: Hex):
        for component in self.components.values():
            component.on_click(clicked_hex)

    def move_to(self, hex_to_go: Hex):
        """telepport the unit to the new location, doesn't check anything. if you want real movement check Component_movement"""
        self.get_hex().unit_on_hex = None
        self.w, self.h = hex_to_go.w, hex_to_go.h
        self.get_hex().unit_on_hex = self
        for component in self.components.values():
            component.after_movemement()
