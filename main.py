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

# инициализация игры
pygame.init()
screen = pygame.display.set_mode(size)
pygame.display.set_caption(window_name)
clock = pygame.time.Clock()

game_folder = os.path.dirname(__file__)
img_folder = os.path.join(game_folder, "data/img")
font_folder = os.path.join(game_folder, "data/fonts")

# bg - background
bg = pygame.image.load(f'{img_folder}/bg.jpg').convert()
bg2 = pygame.image.load(f'{img_folder}/bg2.jpg').convert()
bg2_duplicate = bg2.copy()
bg_menu = pygame.image.load(f'{img_folder}/bg_menu.jpg').convert()
bg_menu = pygame.transform.scale(bg_menu, (width + 400, height))


def on_music(type_of_music):
    if type_of_music == "menu":
        pygame.mixer.music.load(choice(['data/audio/CypherTwin.wav',
                                        'data/audio/MorphadronRezidue.wav']))
    elif type_of_music == "game":
        pygame.mixer.music.load(choice(['data/audio/CypherTwin.wav',
                                        'data/audio/MorphadronRezidue.wav']))
    elif type_of_music == "game_over":
        pygame.mixer.music.load(choice(['data/audio/a1.wav']))
    pygame.mixer.music.set_volume(0.3)
    pygame.mixer.music.play(loops=-1)


def off_music():
    pygame.mixer.pause()


class Player(pygame.sprite.Sprite):
    def __init__(self, x, y, cycle=1):  # cycle - режим игры, 1 - одиночный, 2 - для двоих
        pygame.sprite.Sprite.__init__(self)
        self.width, self.height = 30, 40
        self.cycle = cycle
        # загружаем спрайты для движения игрока
        self.animation_left = [pygame.image.load(f"{img_folder}/walk/player1/walk_left/{i}.png") for i in range(1, 11)]
        self.animation_right = [pygame.image.load(f"{img_folder}/walk/player1/walk_right/{i}.png")
                                for i in range(1, 11)]
        self.animation_stand = [pygame.image.load(f"{img_folder}/walk/player1/stand/{i}.png") for i in range(1, 3)]
        self.animation_jump = [pygame.image.load(f"{img_folder}/walk/player1/jump/{i}.png") for i in range(1, 3)]
        self.image = self.animation_left[0]
        # направление спрайт, l - left, r - right
        self.direction = "l"

        self.rect = self.image.get_rect()
        self.rect.x, self.rect.y = x, y
        # максимальная скорость игрока по оси x
        self.move_speed = 7
        self.speedx = 0  # скорость игрока по оси x
        self.speedy = 0  # скорость игрока по оси y
        # максимальная скорость прыжка
        self.jump_power = 9
        # сила, с которой персонажа притягивает к земле
        self.gravity = 0.35
        self.onground = False   # True - Персонаж стоит на земле
        self.count_anim = 0
        # Число прыжков персонажа
        self.number_of_jumps = 0
        self.max_number_of_jumps = 2

        self.max_height = 0  # максимально набранная высота
        self.management = [pygame.K_LEFT, pygame.K_RIGHT, pygame.K_UP]

    def update(self, objects):
        self.speedx = 0
        if self.direction == "l":
            self.image = self.animation_stand[0]
        else:
            self.image = self.animation_stand[1]
        keypressed = pygame.key.get_pressed()
        # self.move_speed добавляется к скорости а не к координатам x, или y!
        if keypressed[self.management[0]]:
            self.speedx -= self.move_speed
            self.image = self.animation_left[self.count_anim // 3 - 1]
            self.direction = "l"
        if keypressed[self.management[1]]:
            self.speedx += self.move_speed
            self.image = self.animation_right[self.count_anim // 3 - 1]
            self.direction = "r"
        if keypressed[self.management[2]]:
            if self.onground or self.number_of_jumps < self.max_number_of_jumps and self.speedy > 0:
                self.speedy -= self.jump_power
                self.number_of_jumps += 1

        if not self.onground:
            self.speedy += self.gravity

        if self.speedy < 0 and self.direction == "l":
            self.image = self.animation_jump[0]
        if self.speedy < 0 and self.direction == "r":
            self.image = self.animation_jump[1]
        self.onground = False

        # Меняем координаты персонажа в зависимости от скорости
        self.rect.y += self.speedy
        self.collisions(0, self.speedy, objects)

        self.rect.x += self.speedx
        self.collisions(self.speedx, 0, objects)

        self.count_anim += 1
        if self.count_anim == 30:
            self.count_anim = 0
        # Не даём персонажу выйти за границы экрана
        if self.rect.right > width:
            self.rect.right = width
        if self.rect.left < 0:
            self.rect.left = 0
        # Вычисляем максимальную высоту на которую персонаж смог забраться
        self.max_height = max(height - self.rect.y, self.max_height)

    # функция отвечающая за столкновения с объектами, получает скорости по оси x, y и объекты
    def collisions(self, x, y, objects):
        for object in objects:
            if pygame.sprite.collide_rect(self, object):  # При столкновении
                # если персонаж находится на земле и на него падает коробка, заканчиваем игру
                if object.is_flying and y > 0:
                    return game_over(cycle=self.cycle)
                # В зависимости от скорости персонажа и положения объекта, останавливаем персонажа
                if x > 0:
                    self.rect.right = object.rect.left
                if x < 0:
                    self.rect.left = object.rect.right
                if y > 0 and object.rect.y < self.rect.y:
                    self.rect.top = object.rect.bottom
                    self.rect.x += 10
                    self.speedy = 10
                if y > 0:
                    self.rect.bottom = object.rect.top
                    self.onground = True
                    self.number_of_jumps = 0
                    self.speedy = 0
                if y < 0:
                    self.rect.top = object.rect.bottom
                    self.speedy = 8


class Player2(Player, pygame.sprite.Sprite):  # Делаем копию класса Player с замененным управлением и спрайтами
    def __init__(self, x, y, cycle=2):
        pygame.sprite.Sprite.__init__(self)
        Player.__init__(self, x, y, cycle)
        self.animation_left = [pygame.image.load(f"{img_folder}/walk/player2/walk_left/{i}.png") for i in range(1, 11)]
        self.animation_right = [pygame.image.load(f"{img_folder}/walk/player2/walk_right/{i}.png") for i in
                                range(1, 11)]
        self.animation_stand = [pygame.image.load(f"{img_folder}/walk/player2/stand/{i}.png") for i in range(1, 3)]
        self.animation_jump = [pygame.image.load(f"{img_folder}/walk/player2/jump/{i}.png") for i in range(1, 3)]
        self.management = [pygame.K_a, pygame.K_d, pygame.K_w]


class Obstacle(pygame.sprite.Sprite):
    woodenBox50x50 = pygame.image.load(f'{img_folder}/woodenBox50x50.png').convert()
    woodenBox100x50 = pygame.image.load(f'{img_folder}/woodenBox100x50.png').convert()
    metalBoxBlue50x50 = pygame.image.load(f'{img_folder}/metalBoxBlue50x50.png').convert()
    metalBoxBlue100x50 = pygame.image.load(f'{img_folder}/metalBoxBlue100x50.png').convert()
    metalBoxRed50x50 = pygame.image.load(f'{img_folder}/metalBoxRed50x50.png').convert()
    metalBoxRed100x50 = pygame.image.load(f'{img_folder}/metalBoxRed100x50.png').convert()
    metalBoxGray100x100 = pygame.image.load(f'{img_folder}/metalBoxGray100x100.jpg').convert()

    def __init__(self, x, y, w, h, s, type='box'):
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
            self.image = pygame.Surface((w, h))
            self.image.fill(BLACK)
            self.rect = self.image.get_rect()
            self.rect.x, self.rect.y = x, y
        self.type = type
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
    def __init__(self, w, h, inactive_color, active_color):
        self.width, self.height = w, h
        # inactive_color - стандартный цвет кнопки мыши
        # action_color - цвет кнопки при наведении на неё курсора мыши
        self.inactive_color = inactive_color
        self.active_color = active_color

    # action - функция которую нужно выполнить при нажатии на кнопку
    def draw(self, x, y, message, action=None, f_type="NaturalMonoRegular.ttf"):
        mouse = pygame.mouse.get_pos()
        click = pygame.mouse.get_pressed()
        # При наведении курсора меняем цвет кнопки на active_color
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


def game_over(cycle=1):  #
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

        # Заканчиваем игру если персонаж выходит за границы экрана
        if player.rect.y > height:
            running = False
            game_over()
        pygame.display.flip()

    off_music()


if __name__ == '__main__':
    game_menu()
    pygame.quit()
