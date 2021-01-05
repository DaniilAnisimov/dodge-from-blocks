import os
from random import randint, choice
import pygame

# Базовые переменные
size = width, height = 500, 600
window_name = "Dodge from blocks"
fps = 60
# метры
meters = 0
height_meters = 40  # В пикселях
altitude_record = 0

# Цвета
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
RED = (255, 0, 0)
GREEN = (0, 255, 0)
BLUE = (0, 0, 255)
LIGHT_CORAL = (255, 100, 100)

pygame.init()
screen = pygame.display.set_mode(size)
pygame.display.set_caption(window_name)
clock = pygame.time.Clock()

game_folder = os.path.dirname(__file__)
img_folder = os.path.join(game_folder, "img")
font_folder = os.path.join(game_folder, "fonts")

bg = pygame.image.load(f'{img_folder}/bg.jpg').convert()
bg2 = pygame.image.load(f'{img_folder}/bg2.jpg').convert()
bg2_duplicate = bg2.copy()
bg_menu = pygame.image.load(f'{img_folder}/bg_menu.jpg').convert()
bg_menu = pygame.transform.scale(bg_menu, (width + 400, height))


def on_music(type_of_music):
    if type_of_music == "menu":
        pygame.mixer.music.load(choice(['audio/CypherTwin.wav',
                                        'audio/MorphadronRezidue.wav']))
    elif type_of_music == "game":
        pygame.mixer.music.load(choice(['audio/CypherTwin.wav',
                                        'audio/MorphadronRezidue.wav']))
    elif type_of_music == "game_over":
        pygame.mixer.music.load(choice(['audio/a1.wav']))
    pygame.mixer.music.set_volume(0.3)
    pygame.mixer.music.play(loops=-1)


def off_music():
    pygame.mixer.pause()


class Player(pygame.sprite.Sprite):
    def __init__(self, x, y, cycle=1):
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
        self.jump_power = 9
        self.gravity = 0.35
        self.onground = False
        self.count_anim = 0
        self.number_of_jumps = 0
        self.max_number_of_jumps = 2
        self.max_height = 0
        self.cycle = cycle

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
            if self.onground or self.number_of_jumps < self.max_number_of_jumps and self.speedy > 0:
                self.speedy -= self.jump_power
                self.number_of_jumps += 1
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
        if self.rect.right > width:
            self.rect.right = width
        if self.rect.left < 0:
            self.rect.left = 0
        self.max_height = max(height - self.rect.y, self.max_height)

    def collisions(self, x, y, objects):
        for object in objects:
            if pygame.sprite.collide_rect(self, object):
                if object.is_flying and self.onground:
                    game_over(cycle=self.cycle)
                if x > 0:
                    self.rect.right = object.rect.left
                if x < 0:
                    self.rect.left = object.rect.right
                if y > 0 and object.rect.y < self.rect.y:
                    self.rect.top = object.rect.bottom
                    self.speedy = 8
                if y > 0:
                    self.rect.bottom = object.rect.top
                    self.onground = True
                    self.number_of_jumps = 0
                    self.speedy = 0
                if y < 0:
                    self.rect.top = object.rect.bottom
                    self.speedy = 8


class Player2(Player, pygame.sprite.Sprite):
    def __init__(self, x, y, cycle=1):
        pygame.sprite.Sprite.__init__(self)
        Player.__init__(self, x, y, cycle)

    def update(self, objects):
        self.speedx = 0
        keypressed = pygame.key.get_pressed()
        if keypressed[pygame.K_a]:
            self.speedx -= self.move_speed
            self.image = self.animation_left[self.count_anim // 3 - 1]
        if keypressed[pygame.K_d]:
            self.speedx += self.move_speed
            self.image = self.animation_right[self.count_anim // 3 - 1]
        if keypressed[pygame.K_w]:
            if self.onground or self.number_of_jumps < self.max_number_of_jumps and self.speedy > 0:
                self.speedy -= self.jump_power
                self.number_of_jumps += 1
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
        if self.rect.right > width:
            self.rect.right = width
        if self.rect.left < 0:
            self.rect.left = 0
        self.max_height = max(height - self.rect.y, self.max_height)


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
            self.image = choice([Obstacle.woodenBox50x50,
                                 Obstacle.woodenBox100x50,
                                 Obstacle.metalBoxBlue50x50,
                                 Obstacle.metalBoxBlue100x50,
                                 Obstacle.metalBoxRed100x50,
                                 Obstacle.metalBoxRed50x50,
                                 Obstacle.metalBoxGray100x100])
            self.rect = self.image.get_rect()
            if self.rect.width == 100:
                self.rect.x = randint(0, 8) * 50
            else:
                self.rect.x = randint(0, 9) * 50
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


class Button:
    def __init__(self, width, height, inactive_color, active_color):
        self.width, self.height = width, height
        self.inactive_color = inactive_color
        self.active_color = active_color

    def draw(self, x, y, message, action=None, f_type="NaturalMonoRegular.ttf"):
        mouse = pygame.mouse.get_pos()
        click = pygame.mouse.get_pressed()
        if x < mouse[0] < x + self.width and y < mouse[1] < y + self.height:
            draw_text(screen, x, y, message, color=self.active_color, size=self.height, f_type=f_type)
            if click[0] == 1 and action:
                action()
        else:
            draw_text(screen, x, y, message, color=self.inactive_color, size=self.height, f_type=f_type)


# Доступные шрифты: NaturalMonoRegular, PerfectDOSVGA437, RobotronDotMatrix, Thintel
def draw_text(screen, x, y, text, color=BLACK, f_type="NaturalMonoRegular.ttf", size=30):
    font = pygame.font.Font(font_folder + "/" + f_type, size)
    text = font.render(text, True, color)
    screen.blit(text, (x, y))


def game_menu():
    game_button = Button(200, 50, BLACK, BLUE)
    game_for_2_button = Button(500, 50, BLACK, BLUE)
    exit_button = Button(200, 50, BLACK, BLUE)

    on_music("menu")
    running = True
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                exit()

        # Рендеринг
        screen.blit(bg_menu, (0, 0))
        game_button.draw(20, 100, "Играть", game_cycle)
        game_for_2_button.draw(20, 200, "Играть вдвоём", game_cycle_2)
        exit_button.draw(20, 300, "Выйти", exit)
        draw_text(screen, 40, 20, "Dodge from", f_type="PerfectDOSVGA437.ttf", size=40)
        draw_text(screen, 290, 20, "Blocks", f_type="RobotronDotMatrix.otf", size=40)

        pygame.display.update()
        clock.tick(fps - fps // 2)
    off_music()


def pause():
    paused = True
    draw_text(screen, 25, 100, "Пауза. Нажмите p чтобы продолжить.", color=RED, size=22)
    while paused:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                exit()
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_p:
                    paused = False

        pygame.display.update()
        clock.tick(fps)


def game_over(cycle=1):
    running = True
    drawing = True
    screen_saver_speed = 10
    x = 0

    on_music("game_over")

    continue_button = Button(200, 25, (200, 200, 200), WHITE)
    exit_button = Button(100, 25, (200, 200, 200), WHITE)
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                exit()

        screen.fill(BLACK, (0, 0, x, height))
        if x >= width:
            drawing = False
        if drawing:
            x += screen_saver_speed
        else:
            draw_text(screen, 85, 200, "Игра окончена", color=WHITE, size=50, f_type="PerfectDOSVGA437.ttf")
            draw_text(screen, 150, 260, "Рекорд высоты: "
                      + str(altitude_record // height_meters), color=WHITE, size=25, f_type="PerfectDOSVGA437.ttf")
            if cycle == 1:
                continue_button.draw(180, 300, "Новая игра", action=game_cycle)
            else:
                continue_button.draw(180, 300, "Новая игра", action=game_cycle_2)
            exit_button.draw(210, 335, "Выйти", action=game_menu)
        pygame.display.update()
        clock.tick(fps)

    pygame.mixer.pause()


def game_cycle_2():
    global meters, altitude_record
    # самый высокий блок
    top = 0

    altitude_record = 0
    meters = 0

    # сдвиг фона
    delta_x_bg = -100
    delta_y_bg = 0
    first_bg_isEnabled = True

    # Группы
    players = pygame.sprite.Group()
    barrier = pygame.sprite.Group()
    objects = []

    # Мобы
    player = Player(width / 2 + 20, height - 300, cycle=2)
    player2 = Player2(width / 2 - 20, height - 300, cycle=2)
    floor = Obstacle(0, height - 10, width, 10, 0, 'floor')

    objects += [floor]
    for object in objects:
        barrier.add(object)
    players.add(player)
    players.add(player2)

    box = Obstacle(randint(10, width - 60), -100, 50, 50, 5)
    objects.append(box)
    barrier.add(box)

    on_music("game")

    running = True
    while running:
        dt = clock.tick(fps) / 5
        # События
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
                exit()
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_p:
                    pause()

        # Обновление
        players.update(objects)
        barrier.update(objects)

        for box in barrier:
            if box != floor and box.rect.y <= 300 and not box.is_flying:
                top = box.rect.y
        if top:
            for box in barrier:
                box.rect.y += dt
            meters += int(dt)
            delta_y_bg += dt
            player.max_height = 0
            player2.max_height = 0
            top = 0

        if box.speedy == 0:
            box = Obstacle(randint(10, width - 60), -100, 50, 50, 5)
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

        altitude_record = max(meters + player.max_height, altitude_record)
        draw_text(screen, 20, 10, 'meters: ' + str(altitude_record // height_meters), LIGHT_CORAL)

        # возврат фона
        if delta_y_bg >= height:
            delta_y_bg = 0
            if first_bg_isEnabled:
                first_bg_isEnabled = False

        if player.rect.y > height:
            return game_over(cycle=2)
        if player2.rect.y > height:
            return game_over(cycle=2)
        pygame.display.flip()

    off_music()


def game_cycle():
    global meters, altitude_record
    # самый высокий блок
    top = 0

    altitude_record = 0
    meters = 0

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

    objects += [floor]
    for object in objects:
        barrier.add(object)
    players.add(player)

    box = Obstacle(randint(10, width - 60), -100, 50, 50, 5)
    objects.append(box)
    barrier.add(box)

    on_music("game")

    running = True
    while running:
        dt = clock.tick(fps) / 5
        # События
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
                exit()
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_p:
                    pause()

        # Обновление
        players.update(objects)
        barrier.update(objects)

        for box in barrier:
            if box != floor and box.rect.y <= 300 and not box.is_flying:
                top = box.rect.y
        if top:
            for box in barrier:
                box.rect.y += dt
            meters += int(dt)
            delta_y_bg += dt
            player.max_height = 0
            top = 0

        if box.speedy == 0:
            box = Obstacle(randint(10, width - 60), -100, 50, 50, 5)
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

        altitude_record = max(meters + player.max_height, altitude_record)
        draw_text(screen, 20, 10, 'meters: ' + str(altitude_record // height_meters), LIGHT_CORAL)

        # возврат фона
        if delta_y_bg >= height:
            delta_y_bg = 0
            if first_bg_isEnabled:
                first_bg_isEnabled = False

        if player.rect.y > height:
            running = False
            game_over()
        pygame.display.flip()

    off_music()


if __name__ == '__main__':
    game_menu()
    pygame.quit()
