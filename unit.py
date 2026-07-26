from pyg import camera, draw, get_percentage
import pygame as pg
import data, pyg, abc, random, camera_movement
from typing import Type, TYPE_CHECKING
import math

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
    height = 30
    width = 200
    border_size = 2
    font = pg.font.Font(pg.font.get_default_font(), height - (border_size * 2))

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

    def get_surface(self, show_digits: bool = True):
        surface = draw.bar_percentage(
            get_percentage(self.value, self.max_value),
            self.width,
            self.height,
            self.color,
            border_size=self.border_size,
        )
        if show_digits:
            surface.blit(
                draw.text(
                    f"{self.value}/{self.max_value}",
                    "white",
                    Bar.font,
                    pg.Rect(
                        0,
                        0,
                        self.width - (self.border_size * 2),
                        self.height - (self.border_size * 2),
                    ),
                ),
                (self.border_size, self.border_size),
            )
        return surface

    def draw(self, pos: tuple[int, int], show_digit: bool = True):
        camera(
            pg.transform.scale_by(
                self.get_surface(show_digit),
                camera_movement.zoom_level / 2,  # /2 cuz i doubled the height and width
            ),
            pos,
        )


class Component(abc.ABC):
    """Base class for all components"""

    dependency: list[type[Component]] = []

    def __init__(self, unit: "Unit", info: dict[str]):
        self.unit = unit
        self.unit.components[self.get_name()] = self
        for dependency in self.dependency:
            if not self.unit.has_component(dependency):
                raise ValueError(
                    f"Component: {self.__class__.__name__} need the component {dependency.__name__}"
                )

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
        fuel = info.get(Component_movement.FUEL, self.max_fuel)
        self.fuel_bar = Bar("brown", self.max_fuel, fuel)
        self.add_bar(self.fuel_bar)

    def get_info(self):
        return {
            Component_movement.FUEL: self.fuel,
        }

    def on_click(self, hex: Hex):
        if not self.unit.is_selected:
            return
        self.move_to(hex)

    def move_to(self, hex: Hex):
        possible_hexs_to_go = self.get_possible_hexs_to_go()
        if hex.unit_on_hex is not None or hex not in possible_hexs_to_go:
            return

        fuel_after_movement = self.fuel - (
            self.movement_point - possible_hexs_to_go[hex]
        )
        if fuel_after_movement < 0:
            return
        self.fuel = fuel_after_movement
        self.movement_point = possible_hexs_to_go[hex]

        self.unit.move_to(hex)

        if self.unit.has_component(Component_transport):
            component_transport: Component_transport = self.unit.get_component(
                Component_transport
            )
            component_transport.transport_material(self.unit)

    def get_possible_hexs_to_go(self):

        possible_hexs_to_go: dict[Hex, int] = {}
        non_filtered_possible_hexs_to_go = self.unit.get_hex().search_hex(
            self.movement_point, True, False
        )
        for hex in non_filtered_possible_hexs_to_go:
            cost = non_filtered_possible_hexs_to_go[hex]
            if hex.unit_on_hex is not None:
                continue
            possible_hexs_to_go[hex] = cost
        return possible_hexs_to_go

    def step(self):
        if self.unit.is_selected:
            for possible_hex_to_go in self.get_possible_hexs_to_go():
                possible_hex_to_go.draw_surface_on_top(data.hex_can_go)
        return super().step()

    @property
    def fuel(self):
        return self.fuel_bar.value

    @fuel.setter
    def fuel(self, amount: int):
        self.fuel_bar.value = amount
        if self.fuel < 0:
            raise ValueError(f"fuel ({self.fuel}) of unit {self.unit} is negative")


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
        hex.reload_fog_surface()

    def after_movemement(self):
        self.calculate_vision()
        return super().after_movemement()


class Component_attack(Component):
    DAMAGE = "damage"
    AMMO = "ammo"
    MAX_AMMO = "max ammo"
    RANGE = "range"
    attack_button = data.attack_button
    hex_can_attack = data.hex_can_attack

    def __init__(self, unit, info: dict[str]):
        super().__init__(unit, info)
        self.damage = int(unit.get_type_info()[self.DAMAGE])
        self.max_ammo = unit.get_type_info()[self.MAX_AMMO]
        self.ammo = info.get(self.AMMO, self.max_ammo)
        self.attack_range = unit.get_type_info()[self.RANGE]

        self.ammo_bar = Bar("red", self.max_ammo, self.ammo)
        self.has_not_attacked = True

        self.add_bar(self.ammo_bar)

    def on_click(self, hex):
        if self.unit.is_selected:
            self.attack_tile(hex)

        return super().on_click(hex)

    def attack_tile(self, hex: Hex):
        if hex not in self.get_attackable_hexs():
            return

        unit = hex.unit_on_hex
        if (
            (unit is None)
            or (unit.team == self.unit.team)
            or (not unit.has_component(Component_pv))
            or not self.has_not_attacked
        ):
            return

        self.ammo_bar.value -= 1
        pv_component: Component_pv = unit.get_component(Component_pv)
        pv_component.damage(self.damage)
        self.has_not_attacked = False

    def step(self):
        if self.unit.is_selected and self.has_not_attacked:
            self.draw_attackable_hexs()
        return super().step()

    def get_attackable_hexs(self):
        attackable_hexs: list[Hex] = []
        for hex in self.unit.get_hex().search_hex(self.attack_range, False, False):
            if hex.unit_on_hex is None or hex.unit_on_hex.team == self.unit.team:
                continue
            attackable_hexs.append(hex)
        return attackable_hexs

    def draw_attackable_hexs(self):
        for hex in self.get_attackable_hexs():
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


class Component_material(Component):
    MAX_MATERIAL = "max material"
    MATERIAL = "material amount"

    def __init__(self, unit, info):
        super().__init__(unit, info)
        self.max_material = unit.get_type_info()[Component_material.MAX_MATERIAL]

        self.material = int(info.get(Component_material.MATERIAL, 0))
        self.material_bar = Bar("purple", self.max_material, self.material)
        self.add_bar(self.material_bar)

    def change_material(self, amount: int):
        self.material += amount
        if self.material < 0:
            raise ValueError(
                f"can't subtract more than the amount of material {self.material}-{amount}<0"
            )
        self.material_bar.value = self.material

    def get_info(self):
        return {Component_material.MATERIAL: self.material}


class Component_fabricator(Component):
    CAN_CREATE_UNIT = "unit can create"

    unit_selected_to_fabricate: str | None = None

    dependency = [Component_material]

    def __init__(self, unit, info):
        super().__init__(unit, info)

        self.creatable_unit: list[str] = self.unit.get_type_info()[self.CAN_CREATE_UNIT]
        self.init_button()

        self.component_material: Component_material = self.unit.get_component(
            Component_material
        )

    def init_button(self):
        button_background = data.fabricate_unit_background_button
        button_background = pg.transform.scale(button_background, Unit.button_size.size)

        for unit_name in self.creatable_unit:
            button_surface = button_background.copy()
            unit_surface = get_unit_surface((unit_name), self.unit.color)
            unit_surface = pg.transform.scale(unit_surface, Unit.button_size.size)
            button_surface.blit(unit_surface, (0, 0))
            self.test = button_surface
            explanation = f"{unit_type[unit_name][DESCRIPTION]}, cost: {unit_type[unit_name][COST]}"
            self.unit.add_button(
                button_surface,
                Component_fabricator.set_unit_selected_to_fabricate,
                (unit_name,),
                explanation,
            )

    def get_fabrication_hexs(self):
        if self.unit_selected_to_fabricate is not None:
            terrain_required = unit_type[self.unit_selected_to_fabricate].get(
                Component_terain_requirements.REQUIRED_TERRAIN
            )
        else:
            terrain_required = None
        fabrication_hexs: list[Hex] = []
        for hex_around in self.unit.get_hex().get_hexs_around_hex():
            if hex_around.unit_on_hex is not None:
                continue
            if terrain_required is not None and hex_around.type != terrain_required:
                continue
            fabrication_hexs.append(hex_around)

        return fabrication_hexs

    @staticmethod
    def set_unit_selected_to_fabricate(unit_name: str):
        Component_fabricator.unit_selected_to_fabricate = unit_name

    def unit_unselected(self):
        Component_fabricator.unit_selected_to_fabricate = None
        return super().unit_unselected()

    def step(self):
        if (
            self.unit.is_selected
            and Component_fabricator.unit_selected_to_fabricate is not None
        ):
            for hex in self.get_fabrication_hexs():
                hex.draw_surface_on_top(data.hex_can_fabricate)

        return super().step()

    def on_click(self, clicked_hex):
        super().on_click(clicked_hex)
        if not self.unit.is_selected:
            return
        if (
            clicked_hex in self.get_fabrication_hexs()
            and self.unit_selected_to_fabricate is not None
        ):
            self.create_unit(clicked_hex)

    def create_unit(self, hex_to_create: Hex):
        if self.unit_selected_to_fabricate is None:
            raise ValueError(
                f"can't call create unit for {self} with no unit selected to fabricate"
            )

        unit_name_to_create = self.unit_selected_to_fabricate

        if unit_name_to_create not in self.creatable_unit:
            raise ValueError(
                f"{unit_name_to_create} is not in the list of unit {self} can create ({self.creatable_unit})"
            )

        if hex_to_create.unit_on_hex is not None:
            return
        cost = unit_type[unit_name_to_create][COST]
        if cost > self.component_material.material:
            return
        self.component_material.change_material(-cost)
        Unit.from_name(
            hex_to_create.w,
            hex_to_create.h,
            unit_name_to_create,
            self.unit.team,
        )


class Component_transport(Component):
    TRANSPORT_RANGE = "transport range"

    material_to_fuel_conversion = 2
    """The number of fuel gained per material given"""
    material_to_ammo_conversion = 2
    """The number of ammo gained per material given"""

    dependency = [Component_material]

    def __init__(self, unit, info):
        super().__init__(unit, info)
        self.component_material: Component_material = self.unit.get_component(
            Component_material
        )
        self.transport_range = self.unit.get_type_info()[
            Component_transport.TRANSPORT_RANGE
        ]

    def get_transportable_hexs(self):
        transportable_hexs: list[Hex] = []
        for hex in self.unit.get_hex().search_hex(self.transport_range, False, False):
            if hex.unit_on_hex is None or hex.unit_on_hex.team != self.unit.team:
                continue
            transportable_hexs.append(hex)
        return transportable_hexs

    def draw_transportable_hexs(self):
        for hex in self.get_transportable_hexs():
            hex.draw_surface_on_top(data.hex_can_transport)

    def step(self):
        if self.unit.is_selected:
            self.draw_transportable_hexs()

    def on_click(self, clicked_hex):
        unit = clicked_hex.unit_on_hex
        if unit is None:
            return

        if any(
            (
                not self.unit.is_selected,
                unit.team != self.unit.team,
                clicked_hex not in self.get_transportable_hexs(),
            )
        ):
            return
        self.transport_material(unit)

    def transport_material(self, to_unit: Unit, amount=-1):
        """transport material, fuel and ammo to an unit.
        It prioritize fuel then ammo then material.

        Args:
            to_unit (Unit): _description_
            amount (int, optional): keeping to -1 sets the maximum amount possible. Defaults to -1.
        """
        if to_unit.team != self.unit.team:
            raise ValueError(
                f"The unit {to_unit} isn't in the same team as self {self}"
            )
        if to_unit.has_component(Component_movement):
            unit_component_movement: Component_movement = to_unit.get_component(
                Component_movement
            )
            fuel_to_give = min(
                self.component_material.material
                * Component_transport.material_to_fuel_conversion,
                (unit_component_movement.max_fuel - unit_component_movement.fuel),
            )
            unit_component_movement.fuel += fuel_to_give
            self.component_material.change_material(
                -math.ceil(
                    fuel_to_give / Component_transport.material_to_fuel_conversion
                )
            )

        if to_unit.has_component(Component_attack):
            unit_component_attack: Component_attack = to_unit.get_component(
                Component_attack
            )
            ammo_to_give = min(
                self.component_material.material
                * Component_transport.material_to_ammo_conversion,
                (unit_component_attack.max_ammo - unit_component_attack.ammo),
            )
            unit_component_attack.ammo += ammo_to_give
            unit_component_attack.ammo_bar.value = unit_component_attack.ammo
            self.component_material.change_material(
                -math.ceil(
                    ammo_to_give / Component_transport.material_to_ammo_conversion
                )
            )

        if to_unit.has_component(Component_material):
            unit_component_material: Component_material = to_unit.get_component(
                Component_material
            )
            material_to_give = min(
                self.component_material.material,
                (
                    unit_component_material.max_material
                    - unit_component_material.material
                ),
            )
            unit_component_material.material += material_to_give
            unit_component_material.material_bar.value = (
                unit_component_material.material
            )
            self.component_material.change_material(-math.ceil(material_to_give))


class Component_producer(Component):
    dependency = [Component_material]
    MATERIAL_PER_TURN = "material per turn"

    def __init__(self, unit, info):
        super().__init__(unit, info)
        self.component_material: Component_material = self.unit.get_component(
            Component_material
        )
        material_per_turn = self.unit.get_type_info()[
            Component_producer.MATERIAL_PER_TURN
        ]
        self.component_material.change_material(material_per_turn)


class Component_terain_requirements(Component):
    REQUIRED_TERRAIN = "requires terrain"

    def __init__(self, unit, info):
        super().__init__(unit, info)
        self.required_terrain = self.unit.get_type_info()[
            Component_terain_requirements.REQUIRED_TERRAIN
        ]
        self.check_terrain()

    def after_movemement(self):
        self.check_terrain()
        return super().after_movemement()

    def check_terrain(self):
        unit_terrain = self.unit.get_hex().type
        if unit_terrain != self.required_terrain:
            raise ValueError(
                f"Unit {self.unit} needs terrain {self.required_terrain} but is on {unit_terrain}"
            )


component_load_order = [
    Component_terain_requirements,
    Component_pv,
    Component_vision,
    Component_material,
    Component_fabricator,
    Component_producer,
    Component_transport,
    Component_attack,
    Component_movement,
]

SURFACE = "surface"
COMPONENTS = "components"
DESCRIPTION = "description"
COST = "cost"

TANK = "test unit"
USINE = "test usine"
TRUCK = "test truck"
MINER = "test miner"
MOBILE_BUILDER = "mobile builder"

unit_type = {
    USINE: {
        SURFACE: "village.png",
        COMPONENTS: [
            Component_pv,
            Component_vision,
            Component_material,
            Component_transport,
            Component_fabricator,
        ],
        DESCRIPTION: "a basic usine to create most units",
        COST: 40,
        Component_vision.VIEW_RANGE: 5,
        Component_pv.MAX_PV: 10,
        Component_fabricator.CAN_CREATE_UNIT: [
            TANK,
            TRUCK,
            MOBILE_BUILDER,
        ],
        Component_material.MAX_MATERIAL: 100,
        Component_transport.TRANSPORT_RANGE: 2,
    },
    TANK: {
        SURFACE: "tank.png",
        COMPONENTS: [
            Component_pv,
            Component_movement,
            Component_vision,
            Component_attack,
        ],
        DESCRIPTION: "a basic tank",
        COST: 15,
        Component_movement.MOVEMENT_POINT: 3,
        Component_movement.MAX_FUEL: 10,
        Component_vision.VIEW_RANGE: 4,
        Component_pv.MAX_PV: 20,
        Component_attack.DAMAGE: 5,
        Component_attack.MAX_AMMO: 20,
        Component_attack.RANGE: 5,
    },
    TRUCK: {
        SURFACE: "truck.png",
        COMPONENTS: [
            Component_pv,
            Component_movement,
            Component_vision,
            Component_material,
            Component_transport,
        ],
        Component_movement.MOVEMENT_POINT: 6,
        Component_movement.MAX_FUEL: 30,
        Component_vision.VIEW_RANGE: 6,
        Component_pv.MAX_PV: 5,
        Component_material.MAX_MATERIAL: 200,
        Component_transport.TRANSPORT_RANGE: 2,
        DESCRIPTION: "a basic truck to transport material",
        COST: 30,
    },
    MINER: {
        SURFACE: "oil_rig.png",
        COMPONENTS: [
            Component_pv,
            Component_material,
            Component_transport,
            Component_producer,
            Component_terain_requirements,
        ],
        Component_pv.MAX_PV: 30,
        Component_material.MAX_MATERIAL: 30,
        Component_transport.TRANSPORT_RANGE: 2,
        Component_producer.MATERIAL_PER_TURN: 10,
        DESCRIPTION: "a farm that create materials each turn, can only be placed on grass",
        COST: 15,
        Component_terain_requirements.REQUIRED_TERRAIN: data.OIL,
    },
    MOBILE_BUILDER: {
        SURFACE: "truck_crane.png",
        COMPONENTS: [
            Component_pv,
            Component_vision,
            Component_movement,
            Component_material,
            Component_transport,
            Component_fabricator,
        ],
        Component_pv.MAX_PV: 10,
        Component_material.MAX_MATERIAL: 50,
        Component_transport.TRANSPORT_RANGE: 2,
        Component_vision.VIEW_RANGE: 3,
        Component_movement.MOVEMENT_POINT: 5,
        Component_movement.MAX_FUEL: 20,
        Component_fabricator.CAN_CREATE_UNIT: [
            MINER,
            USINE,
        ],
        DESCRIPTION: "a constructor to build buildings",
        COST: 20,
    },
}


def get_unit_surface(unit_name: str, color: str):
    image_name = unit_type[unit_name][SURFACE]
    return pg.image.load(data.directory_unit_team_color + color + "_" + image_name)


class Unit:
    all_units: list["Unit"] = []
    unit_selected: None | "Unit" = None

    color_remaining = data.all_colors
    selected_bad_unit_sound = data.selected_bad_unit_sound

    button_size = pg.Rect(0, 0, 50, 50)

    explanation_rect = pg.Rect(0, 0, 400, 800)
    explanation_border_rect_text = 20
    """the border between the nine sided and the text"""

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

        self.id = self.__hash__()
        self.name = info[Unit.NAME]
        self.team = info[Unit.TEAM]
        self.set_color()
        self.set_image()

        if self.get_hex().unit_on_hex != None:
            raise ValueError(
                f"hex({w,h}) is arleady taken by {self.get_hex().unit_on_hex}, can't generate here"
            )
        self.get_hex().unit_on_hex = self

        self.is_selected = False

        self.components: dict[str, Component] = {}
        self.bars: list[Bar] = []
        self.all_buttons: list[pyg.Button] = []
        self.all_explanations: list[pyg.Explain_bubble] = []
        Unit.all_units.append(self)
        components_to_load = unit_type[self.name][COMPONENTS]
        for component in component_load_order:
            if component in components_to_load:
                self.add_component(component, info)

    TEAM = "team"
    NAME = "name"

    def get_info(self):
        """return a dict with all the informations to create a new unit"""
        info = {Unit.TEAM: self.team, Unit.NAME: self.name}
        for component in self.components.values():
            info = info | component.get_info()
        return info

    @classmethod
    def get_all_info(cls):
        all_info: dict[tuple[int, int]] = {}
        for unit in Unit.all_units:
            all_info[pyg.wh_to_string(unit.w, unit.h)] = unit.get_info()
        return all_info

    @classmethod
    def load_all_info(cls, info: dict[str, dict[str,]]):
        for unit_pos in info:
            unit = info[unit_pos]
            unit_w, unit_h = pyg.string_to_wh(unit_pos)
            Unit(unit_w, unit_h, unit)

    def get_type_info(self):
        return unit_type[self.name]

    def set_image(self):
        self.surface = get_unit_surface(self.name, self.color)

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
        all_units = (
            Unit.all_units.copy()
        )  # to avoid side effect of unit.destroy removing element
        for unit in all_units:
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
        self.get_hex().draw_surface_on_top(self.surface)

    def draw_info(self):
        x, y = self.get_xy()
        show_value = camera_movement.zoom_level >= 1
        for i, bar in enumerate(self.bars):
            pos = (
                x,
                y
                - (
                    ((i * Bar.height) + (i * Bar.border_size))
                    * camera_movement.zoom_level
                    / 2  # /2 cuz i doubled the height and width
                ),
            )
            bar.draw(pos, show_value)

    def add_button(
        self,
        surface: pg.Surface,
        function: "function",
        args: tuple = (),
        explanation: str | None = None,
    ):
        rect = Unit.button_size.copy()
        rect.x = (
            len(self.all_buttons) + 1
        ) * Unit.button_size.width  # +1 for the pass turn button
        button = pyg.Button(surface, function, rect, args)
        button.is_visible = False
        self.all_buttons.append(button)

        if explanation is not None:

            text_surface = pyg.draw.text(
                explanation,
                pg.Color(0, 0, 0),
                rect_to_write_on=pg.Rect(
                    (
                        Unit.explanation_border_rect_text,
                        Unit.explanation_border_rect_text,
                    ),
                    Unit.explanation_rect.size,
                ),
            )
            explain_surface_rect = text_surface.get_bounding_rect()
            explain_surface_rect.inflate_ip(
                Unit.explanation_border_rect_text * 2,
                Unit.explanation_border_rect_text * 2,
            )
            explain_surface = data.nine_sided_explanation.get_surface(
                explain_surface_rect
            )
            explain_surface.blit(
                text_surface,
                (Unit.explanation_border_rect_text, Unit.explanation_border_rect_text),
            )

            self.all_explanations.append(pyg.Explain_bubble(rect, explain_surface))

    def get_hex(self):
        """Get the hex where the unit is"""
        from hex import Hex

        return Hex.get_hex_by_wh(self.w, self.h)

    def get_xy(self):
        return self.get_hex().pos

    def select(self):
        if Unit.unit_selected is not None:
            Unit.unit_selected.unselect()
        if self.is_selected:
            raise ValueError(
                f"you can't select a unit that is arleady selected, (unit selected:{ self.__str__()})",
            )

        if self.team != Unit.team_of_main:
            Unit.selected_bad_unit_sound.play()
            return

        for button in self.all_buttons:
            button.is_visible = True
        for explanation in self.all_explanations:
            explanation.is_visible = True
        self.is_selected = True
        Unit.unit_selected = self
        for component in self.components.values():
            component.unit_selected()

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
        for explanation in self.all_explanations:
            explanation.is_visible = False
        data.current_state = data.click_state.SELECT_UNIT

    def on_click(self, clicked_hex: Hex):
        for component in self.components.values():
            component.on_click(clicked_hex)
        self.unselect()

    def move_to(self, hex_to_go: Hex):
        """telepport the unit to the new location, doesn't check anything. if you want real movement check Component_movement"""
        self.get_hex().unit_on_hex = None
        self.w, self.h = hex_to_go.w, hex_to_go.h
        self.get_hex().unit_on_hex = self
        for component in self.components.values():
            component.after_movemement()
