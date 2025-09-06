import pygame


class keyboard:

    pressed_keys = []
    mouse_position = pygame.Vector2(pygame.mouse.get_pos())

    click_map = {
        0: "left click",
        1: "right click",
        2: "middle click",
        3: "fourth click",  # the button on the side that's near the hand (fourth button)
        4: "fifth click",  # the button on the side that's far to the hand (fifth button)
    }

    def key_press(self, key):
        self.pressed_keys.append(pygame.key.name(key))

    def key_release(self, key):
        self.pressed_keys.remove(pygame.key.name(key))

    def step(self):

        self.mouse_position = pygame.Vector2(pygame.mouse.get_pos())

        clicks_pressed = pygame.mouse.get_pressed(5)

        for click_checked in range(5):

            if clicks_pressed[click_checked]:
                if self.click_map[click_checked] not in self.pressed_keys:
                    self.pressed_keys.append(self.click_map[click_checked])

            elif self.click_map[click_checked] in self.pressed_keys:
                self.pressed_keys.remove(self.click_map[click_checked])


class camera:

    rect = pygame.display.get_surface().get_rect()

    screen = pygame.Surface((rect.width, rect.height))

    def reset_screen(self):  # must be called
        self.screen.fill("black")

    def show_on_camera(
        self, image: pygame.Surface, destination: pygame.Rect | tuple[int, int]
    ):
        if isinstance(destination, tuple):
            destination = image.get_rect(x=destination[0], y=destination[1])

        relative_destination = pygame.Rect(
            destination.x - self.rect.x,
            destination.y - self.rect.y,
            destination.width,
            destination.height,
        )

        if self.rect.colliderect(
            destination
        ):  # check if it's in the screen (optimization)
            pygame.display.get_surface().blit(image, relative_destination)
