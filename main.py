import pygame
import random
import os

# Базовые переменные
size = width, height = 500, 600
window_name = "Dodge from blocks"
fps = 60

# Цвета
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
RED = (255, 0, 0)
GREEN = (0, 255, 0)
BLUE = (0, 0, 255)


class Player(pygame.sprite.Sprite):
    def __init__(self, x, y):
        pygame.sprite.Sprite.__init__(self)
        self.width, self.height = 30, 40
        self.image = pygame.Surface((self.width, self.height))
        self.image.fill(RED)
        self.rect = self.image.get_rect()
        self.rect.x, self.rect.y = x, y
        self.move_speed = 10
        self.speedx = 0
        self.speedy = 0
        self.jump_power = 10
        self.gravity = 0.35
        self.onground = False

    def update(self, objects):
        self.speedx = 0
        keypressed = pygame.key.get_pressed()
        if keypressed[pygame.K_LEFT]:
            self.speedx -= self.move_speed
        if keypressed[pygame.K_RIGHT]:
            self.speedx += self.move_speed
        if keypressed[pygame.K_UP]:
            if self.onground:
                self.speedy -= self.jump_power
        if not self.onground:
            self.speedy += self.gravity
        self.onground = False

        self.rect.y += self.speedy
        self.collisions(0, self.speedy, objects)

        self.rect.x += self.speedx
        self.collisions(self.speedx, 0, objects)

    def collisions(self, x, y, objects):
        for object in objects:
            if pygame.sprite.collide_rect(self, object):
                if x > 0:
                    self.rect.right = object.rect.left
                if x < 0:
                    self.rect.left = object.rect.right
                if y > 0:
                    self.rect.bottom = object.rect.top
                    self.onground = True
                    self.speedy = 0
                if y < 0:
                    self.rect.top = object.rect.bottom
                    self.speedy = 0


class Obstacle(pygame.sprite.Sprite):
    def __init__(self, x, y, w, h, s):
        pygame.sprite.Sprite.__init__(self)
        self.image = pygame.Surface((w, h))
        self.image.fill(BLUE)
        self.rect = self.image.get_rect()
        self.rect.x, self.rect.y = x, y
        self.speedy = s

    def update(self, objects):
        self.rect.y += self.speedy
        self.collisions(self.speedy, objects)

    def collisions(self, y, objects):
        for object in objects:
            if self != object and pygame.sprite.collide_rect(self, object):
                if y > 0:
                    self.rect.bottom = object.rect.top
                    self.speedy = 0


def main():
    # Окно игры
    pygame.init()
    pygame.display.set_caption(window_name)
    screen = pygame.display.set_mode(size)
    clock = pygame.time.Clock()

    # Спрайты
    game_folder = os.path.dirname(__file__)
    img_folder = os.path.join(game_folder, "img")

    # Группы
    players = pygame.sprite.Group()
    barrier = pygame.sprite.Group()
    objects = []

    # Мобы
    player = Player(width / 2, height - 80)

    floor = Obstacle(0, height - 10, width, 10, 0)
    left_wall = Obstacle(0, 0, 10, height, 0)
    right_wall = Obstacle(width - 10, 0, 10, height, 0)

    objects += [floor, left_wall, right_wall]
    for object in objects:
        barrier.add(object)
    players.add(player)

    box = Obstacle(random.randint(10, width - 60), -100, 50, 50, 5)
    objects.append(box)
    barrier.add(box)

    running = True
    while running:
        clock.tick(fps)
        # События
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

        # Обновление
        players.update(objects)
        barrier.update(objects)

        if box.speedy == 0:
            box = Obstacle(random.randint(10, width - 60), -100, 50, 50, 5)
            objects.append(box)
            barrier.add(box)

        # Рендеринг
        screen.fill(BLACK)
        players.draw(screen)
        barrier.draw(screen)

        pygame.display.flip()
    pygame.quit()


if __name__ == '__main__':
    main()

