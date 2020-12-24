import os
import random

import pygame

# Базовые переменные
size = width, height = 500, 600
window_name = "Dodge from blocks"
fps = 60
# метры
meters = 0

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
bg2 = pygame.image.load(f'{img_folder}/bg2.jpg').convert()
bg2_duplicate = bg2.copy()


class Player(pygame.sprite.Sprite):
    def __init__(self, x, y):
        pygame.sprite.Sprite.__init__(self)
        self.width, self.height = 30, 40

        self.animation_left = [pygame.image.load(f"{img_folder}/walk/walk_left/{i}.png") for i in range(1, 10)]
        self.animation_right = [pygame.image.load(f"{img_folder}/walk/walk_right/{i}.png") for i in range(1, 10)]
        self.image = self.animation_left[0]
        self.rect = self.image.get_rect()
        self.rect.x, self.rect.y = x, y
        self.move_speed = 8
        self.speedx = 0
        self.speedy = 0
        self.jump_power = 10
        self.jump_power_low = 6
        self.gravity = 0.35
        self.onground = False
        self.count_anim = 0

    def update(self, objects):
        self.speedx = 0
        keypressed = pygame.key.get_pressed()
        if keypressed[pygame.K_LEFT]:
            self.speedx -= self.move_speed
            self.image = self.animation_left[self.count_anim // 3 - 1]
        if keypressed[pygame.K_RIGHT]:
            self.speedx += self.move_speed
            self.image = self.animation_right[self.count_anim // 3 - 1]
        if keypressed[pygame.K_UP]:
            if self.onground:
                self.speedy -= self.jump_power
        if keypressed[pygame.K_SPACE]:
            if self.onground:
                self.speedy -= self.jump_power_low
        if not self.onground:
            self.speedy += self.gravity
        self.onground = False

        self.rect.y += self.speedy
        self.collisions(0, self.speedy, objects)

        self.rect.x += self.speedx
        self.collisions(self.speedx, 0, objects)

        self.count_anim += 1
        if self.count_anim == 30:
            self.count_anim = 0

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
                if object.is_flying:
                    # Потом будем заканчивать игру
                    print('коробка упала сверху')


class Obstacle(pygame.sprite.Sprite):
    woodenBox50x50 = pygame.image.load(f'{img_folder}/woodenBox50x50.png').convert()
    woodenBox100x50 = pygame.image.load(f'{img_folder}/woodenBox100x50.png').convert()
    metalBoxBlue50x50 = pygame.image.load(f'{img_folder}/metalBoxBlue50x50.png').convert()
    metalBoxBlue100x50 = pygame.image.load(f'{img_folder}/metalBoxBlue100x50.png').convert()
    metalBoxRed50x50 = pygame.image.load(f'{img_folder}/metalBoxRed50x50.png').convert()
    metalBoxRed100x50 = pygame.image.load(f'{img_folder}/metalBoxRed100x50.png').convert()
    metalBoxGray100x100 = pygame.image.load(f'{img_folder}/metalBoxGray100x100.jpg').convert()

    def __init__(self, x, y, width, height, s, type='box'):
        pygame.sprite.Sprite.__init__(self)
        self.is_flying = False
        if type == "box":
            self.is_flying = True
            self.image = random.choice([Obstacle.woodenBox50x50,
                                        Obstacle.woodenBox100x50,
                                        Obstacle.metalBoxBlue50x50,
                                        Obstacle.metalBoxBlue100x50,
                                        Obstacle.metalBoxRed100x50,
                                        Obstacle.metalBoxRed50x50,
                                        Obstacle.metalBoxGray100x100])
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

    def update(self, objects):
        self.rect.y += self.speedy
        self.collisions(self.speedy, objects)
        if self.rect.y >= height and self.is_flying:
            self.rect.bottom = self.rect.top
            self.speedy = 0
            self.is_flying = False

    def collisions(self, y, objects):
        for object in objects:
            if self != object and pygame.sprite.collide_rect(self, object):
                if y > 0:
                    self.rect.bottom = object.rect.top
                    self.speedy = 0
                    self.is_flying = False


def draw_meters(screen, x, y, text):
    font = pygame.font.Font(None, 30)
    text = font.render(text, True, (255, 100, 100))
    screen.blit(text, (x, y))


def main():
    global meters
    # самый высокий блок
    top = 0

    # сдвиг фона
    delta_x_bg = -100
    delta_y_bg = 0
    first_bg_isEnabled = True

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
        dt = clock.tick(fps) / 5
        # События
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

        # Обновление
        players.update(objects)
        barrier.update(objects)

        for box in barrier:
            if box != floor and box != left_wall and box != right_wall:
                if box.rect.y <= 300 and not box.is_flying:
                    top = box.rect.y
        if top:
            for box in barrier:
                if box != left_wall and box != right_wall:
                    box.rect.y += dt
            meters += int(dt)
            delta_y_bg += dt
            top = 0

        if box.speedy == 0:
            box = Obstacle(random.randint(10, width - 60), -100, 50, 50, 5)
            objects.append(box)
            barrier.add(box)

        for obj in objects:
            if obj.rect.y >= 1000:
                objects.remove(obj)

        # Рендеринг
        screen.fill(BLACK)
        if first_bg_isEnabled:
            screen.blit(bg, (delta_x_bg, delta_y_bg))
        else:
            screen.blit(bg2_duplicate, (0, delta_y_bg))
        screen.blit(bg2, (0, -(height - delta_y_bg)))
        players.draw(screen)
        barrier.draw(screen)
        draw_meters(screen, 20, 10, 'meters: ' + str(meters))

        # возврат фона
        if delta_y_bg >= height:
            delta_y_bg = 0
            if first_bg_isEnabled:
                first_bg_isEnabled = False

        if player.rect.y > height:
            print('game over')

        pygame.display.flip()
    pygame.quit()


if __name__ == '__main__':
    main()
