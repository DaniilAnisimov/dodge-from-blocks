import os
import random

import pygame

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

pygame.init()
screen = pygame.display.set_mode(size)
pygame.display.set_caption(window_name)
clock = pygame.time.Clock()

game_folder = os.path.dirname(__file__)
img_folder = os.path.join(game_folder, "img")
bg = pygame.image.load(f'{img_folder}/bg.jpg').convert()


class Player(pygame.sprite.Sprite):
    player_image = pygame.image.load(f'{img_folder}/character.png').convert()

    def __init__(self, x, y):
        pygame.sprite.Sprite.__init__(self)
        self.width, self.height = 30, 40
        self.image = Player.player_image
        self.image.set_colorkey(WHITE)
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
    count = 0
    woodenBox50x50 = pygame.image.load(f'{img_folder}/woodenBox50x50.png').convert()
    woodenBox100x50 = pygame.image.load(f'{img_folder}/woodenBox100x50.png').convert()
    metalBoxBlue50x50 = pygame.image.load(f'{img_folder}/metalBoxBlue50x50.png').convert()
    metalBoxBlue100x50 = pygame.image.load(f'{img_folder}/metalBoxBlue100x50.png').convert()
    metalBoxRed50x50 = pygame.image.load(f'{img_folder}/metalBoxRed50x50.png').convert()
    metalBoxRed100x50 = pygame.image.load(f'{img_folder}/metalBoxRed100x50.png').convert()

    def __init__(self, x, y, width, height, s, type='box'):
        pygame.sprite.Sprite.__init__(self)
        self.is_fly = True
        if type == "box":
            self.image = random.choice([Obstacle.woodenBox50x50,
                                        Obstacle.woodenBox100x50,
                                        Obstacle.metalBoxBlue50x50,
                                        Obstacle.metalBoxBlue100x50,
                                        Obstacle.metalBoxRed100x50,
                                        Obstacle.metalBoxRed50x50])
            self.rect = self.image.get_rect()
            if self.rect.width == 100:
                self.rect.x = random.randint(0, 8) * 50
            else:
                self.rect.x = random.randint(0, 9) * 50
        else:
            self.image = pygame.Surface((width, height))
            self.image.fill(BLACK)
            self.rect = self.image.get_rect()
            self.rect.x, self.rect.y = x, y

        self.speedy = s
        Obstacle.count += 1

    def update(self, objects):
        self.rect.y += self.speedy
        self.collisions(self.speedy, objects)

    def collisions(self, y, objects):
        for object in objects:
            if self != object and pygame.sprite.collide_rect(self, object):
                if y > 0:
                    self.rect.bottom = object.rect.top
                    self.speedy = 0
                    self.is_fly = False


def draw_meters(screen, x, y, text):
    font = pygame.font.Font(None, 30)
    text = font.render(text, True, (255, 100, 100))
    screen.blit(text, (x, y))


def main():
    # метры
    meters = 0
    top = 0

    # сдвиг фона
    delta_x_bg = -100
    delta_y_bg = 0

    # Группы
    players = pygame.sprite.Group()
    barrier = pygame.sprite.Group()
    objects = []

    # Мобы
    player = Player(width / 2, height - 300)

    floor = Obstacle(0, height - 10, width, 10, 0, 'floor')
    left_wall = Obstacle(0, 0, 0, height, 0, 'wall')
    right_wall = Obstacle(width, 0, 0, height, 0, 'wall')

    objects += [floor, left_wall, right_wall]
    for object in objects:
        barrier.add(object)
    players.add(player)

    box = Obstacle(random.randint(10, width - 60), -100, 50, 50, 5)
    objects.append(box)
    barrier.add(box)

    running = True
    while running:
        dt = clock.tick(fps) / 10
        # События
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

        # Обновление
        players.update(objects)
        barrier.update(objects)

        for box in barrier:
            if box != floor and box != left_wall and box != right_wall:
                if box.rect.y <= 200 and not box.is_fly:
                    top = box.rect.y
        if top:
            for box in barrier:
                if box != floor and box != left_wall and box != right_wall:
                    print(dt)
                    box.rect.y += dt  # height - player.rect.y
            meters += int(dt)
            top = 0

        if box.speedy == 0:
            box = Obstacle(random.randint(10, width - 60), -100, 50, 50, 5)
            objects.append(box)
            barrier.add(box)

        for obj in objects:
            if obj.rect.y <= -200:
                objects.remove(obj)

        # Рендеринг
        screen.fill(BLACK)
        screen.blit(bg, (delta_x_bg, delta_y_bg))
        players.draw(screen)
        barrier.draw(screen)
        draw_meters(screen, 20, 10, 'meters: ' + str(meters))

        pygame.display.flip()
    pygame.quit()


if __name__ == '__main__':
    main()
