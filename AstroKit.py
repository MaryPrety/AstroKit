import pygame
import random
from PIL import Image
import os
import json

# Инициализация Pygame
pygame.init()

# Размеры окна
WIDTH, HEIGHT = 800, 600
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Космический корабль")

# Цвета
SPACE = (77, 49, 74)
STARS = (252, 217, 225)
SHADOWS = (255, 102, 178)
EXPLOSIONS = (91, 239, 220)
BULLET_COLOR = (176, 220, 215)

# Загрузка шрифта Epilepsy Sans
font_path = 'assets/fonts/EpilepsySans.ttf'
font = pygame.font.Font(font_path, 36)

# Загрузка изображений
spaceship_img = pygame.image.load('assets/spaceship/spaceship.png')
bullet_img = pygame.image.load('assets/bullets/bullet.png')
cry_imgs = [pygame.image.load(f'assets/spaceship/cry/{i}.png') for i in range(1, 3)]
resource_asteroid_imgs = [pygame.image.load(f'assets/asteroids/resource/{i}.png') for i in range(1, 4)]
obstacle_asteroid_imgs = [pygame.image.load(f'assets/asteroids/obstacle/{i}.png') for i in range(1, 5)]
heart_img = pygame.image.load('assets/hearts/heart.png')
exploding_asteroid_imgs = [pygame.image.load(f'assets/asteroids/exploding/{i}.png') for i in range(1, 5)]

# Загрузка GIF-анимаций с использованием PIL
def load_gif(path):
    gif = Image.open(path)
    frames = []
    try:
        while True:
            gif.seek(gif.tell() + 1)
            frame = gif.convert("RGBA")
            pygame_image = pygame.image.fromstring(frame.tobytes(), frame.size, frame.mode)
            frames.append(pygame_image)
    except EOFError:
        pass
    return frames

win_gif = load_gif('assets/win_gif.gif')
lose_gif = load_gif('assets/lose_gif.gif')

# Загрузка звуков
pygame.mixer.music.load('assets/music/background_music.mp3')  # Фоновая музыка
pygame.mixer.music.play(-1)
shoot_sound = pygame.mixer.Sound('assets/sounds/shoot.wav')
cry_sound = pygame.mixer.Sound('assets/sounds/cry.wav')
explosion_sound = pygame.mixer.Sound('assets/sounds/explosion.wav')
game_over_sound = pygame.mixer.Sound('assets/sounds/game_over.wav')
win_sound = pygame.mixer.Sound('assets/sounds/win.wav')
resource_collision_sound = pygame.mixer.Sound('assets/sounds/resource_collision.wav')
obstacle_collision_sound = pygame.mixer.Sound('assets/sounds/obstacle_collision.wav')
empty_shot_sound = pygame.mixer.Sound('assets/sounds/empty_shot.wav')

# Класс космического корабля
class Spaceship:
    def __init__(self):
        self.x = WIDTH // 2
        self.y = HEIGHT - 100
        self.speed = 5
        self.image = spaceship_img
        self.cry_index = 0
        self.lives = 3
        self.crying = False
        self.cry_timer = 0
        self.reload_time = 10  # Время перезарядки между выстрелами в кадрах (0.33 секунды при 30 FPS)
        self.reload_timer = 0

    def move_left(self):
        self.x -= self.speed
        if self.x < 0:
            self.x = 0

    def move_right(self):
        self.x += self.speed
        if self.x > WIDTH - 50:
            self.x = WIDTH - 50

    def move_up(self):
        self.y -= self.speed
        if self.y < 0:
            self.y = 0

    def move_down(self):
        self.y += self.speed
        if self.y > HEIGHT - 50:
            self.y = HEIGHT - 50

    def draw(self):
        if self.crying:
            screen.blit(cry_imgs[self.cry_index], (self.x, self.y))
            self.cry_timer -= 1
            if self.cry_timer <= 0:
                self.crying = False
        else:
            screen.blit(self.image, (self.x, self.y))

    def cry(self):
        self.crying = True
        self.cry_index = (self.cry_index + 1) % 2
        self.cry_timer = 60  # 2 секунды при 30 FPS
        cry_sound.play()

    def reload(self):
        if self.reload_timer > 0:
            self.reload_timer -= 1

# Класс пули
class Bullet:
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.speed = 10
        self.image = bullet_img

    def move(self):
        self.y -= self.speed

    def draw(self):
        screen.blit(self.image, (self.x, self.y))

# Класс кратера с ресурсами
class ResourceCrater:
    def __init__(self):
        self.x = random.randint(0, WIDTH - 50)
        self.y = random.randint(-HEIGHT, 0)
        self.speed = random.randint(1, 3)
        self.images = resource_asteroid_imgs
        self.exploding_images = exploding_asteroid_imgs
        self.frame = 0
        self.hits = 0
        self.exploding = False
        self.explosion_frame = 0

    def move(self):
        if not self.exploding:
            self.y += self.speed
            if self.y > HEIGHT:
                self.reset()

    def reset(self):
        self.x = random.randint(0, WIDTH - 50)
        self.y = random.randint(-HEIGHT, 0)
        self.speed = random.randint(1, 3)
        self.frame = 0
        self.hits = 0
        self.exploding = False
        self.explosion_frame = 0

    def draw(self):
        if self.exploding:
            if self.explosion_frame < len(self.exploding_images):
                screen.blit(self.exploding_images[self.explosion_frame], (self.x, self.y))
                self.explosion_frame += 1
            else:
                self.reset()
        else:
            screen.blit(self.images[self.frame], (self.x, self.y))
            self.frame = (self.frame + 1) % len(self.images)

# Класс кратера-препятствия
class ObstacleCrater:
    def __init__(self):
        self.x = random.randint(0, WIDTH - 50)
        self.y = random.randint(-HEIGHT, 0)
        self.speed = random.randint(1, 5)
        self.images = obstacle_asteroid_imgs
        self.exploding_images = exploding_asteroid_imgs
        self.frame = 0
        self.hits = 0
        self.exploding = False
        self.explosion_frame = 0

    def move(self):
        if not self.exploding:
            self.y += self.speed
            if self.y > HEIGHT:
                self.reset()

    def reset(self):
        self.x = random.randint(0, WIDTH - 50)
        self.y = random.randint(-HEIGHT, 0)
        self.speed = random.randint(1, 5)
        self.frame = 0
        self.hits = 0
        self.exploding = False
        self.explosion_frame = 0

    def draw(self):
        if self.exploding:
            if self.explosion_frame < len(self.exploding_images):
                screen.blit(self.exploding_images[self.explosion_frame], (self.x, self.y))
                self.explosion_frame += 1
            else:
                self.reset()
        else:
            screen.blit(self.images[self.frame], (self.x, self.y))
            self.frame = (self.frame + 1) % len(self.images)

# Функция для сохранения результатов
def save_results(score, collected_planets):
    results = []
    if os.path.exists('results.json'):
        with open('results.json', 'r') as file:
            results = json.load(file)
    results.append({"score": score, "collected_planets": collected_planets})
    with open('results.json', 'w') as file:
        json.dump(results, file)

# Функция для удаления результатов
def delete_results():
    if os.path.exists('results.json'):
        os.remove('results.json')

# Функция для отображения главного меню
def main_menu():
    menu_running = True
    selected_option = 0
    while menu_running:
        screen.fill(SPACE)
        text_title = font.render("Космический корабль", True, STARS)
        text_start = font.render("1. Начать игру", True, STARS)
        text_exit = font.render("2. Выйти", True, STARS)
        text_results = font.render("3. Результаты", True, STARS)
        text_delete_results = font.render("4. Удалить результаты", True, STARS)

        screen.blit(text_title, (WIDTH // 2 - text_title.get_width() // 2, 100))
        screen.blit(text_start, (WIDTH // 2 - text_start.get_width() // 2, 200))
        screen.blit(text_exit, (WIDTH // 2 - text_exit.get_width() // 2, 300))
        screen.blit(text_results, (WIDTH // 2 - text_results.get_width() // 2, 400))
        screen.blit(text_delete_results, (WIDTH // 2 - text_delete_results.get_width() // 2, 500))

        # Выделение выбранного пункта меню
        if selected_option == 0:
            pygame.draw.rect(screen, STARS, (WIDTH // 2 - text_start.get_width() // 2 - 10, 200, text_start.get_width() + 20, text_start.get_height()), 2)
        elif selected_option == 1:
            pygame.draw.rect(screen, STARS, (WIDTH // 2 - text_exit.get_width() // 2 - 10, 300, text_exit.get_width() + 20, text_exit.get_height()), 2)
        elif selected_option == 2:
            pygame.draw.rect(screen, STARS, (WIDTH // 2 - text_results.get_width() // 2 - 10, 400, text_results.get_width() + 20, text_results.get_height()), 2)
        elif selected_option == 3:
            pygame.draw.rect(screen, STARS, (WIDTH // 2 - text_delete_results.get_width() // 2 - 10, 500, text_delete_results.get_width() + 20, text_delete_results.get_height()), 2)

        pygame.display.flip()

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                menu_running = False
                pygame.quit()
                return
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_w:
                    selected_option = (selected_option - 1) % 4
                elif event.key == pygame.K_s:
                    selected_option = (selected_option + 1) % 4
                elif event.key == pygame.K_SPACE:
                    if selected_option == 0:
                        menu_running = False
                        game_loop()
                    elif selected_option == 1:
                        menu_running = False
                        pygame.quit()
                        return
                    elif selected_option == 2:
                        show_results()
                    elif selected_option == 3:
                        delete_results()

# Функция для отображения результатов
def show_results():
    results_running = True
    results = []
    if os.path.exists('results.json'):
        with open('results.json', 'r') as file:
            results = json.load(file)

    while results_running:
        screen.fill(SPACE)
        text_title = font.render("Результаты", True, STARS)
        screen.blit(text_title, (WIDTH // 2 - text_title.get_width() // 2, 50))

        y_offset = 100
        for i, result in enumerate(results):
            text_result = font.render(f"{i + 1}. Score: {result['score']}, Planets: {result['collected_planets']}", True, STARS)
            screen.blit(text_result, (WIDTH // 2 - text_result.get_width() // 2, y_offset))
            y_offset += 40

        pygame.display.flip()

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                results_running = False
                pygame.quit()
                return
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    results_running = False
                    main_menu()

# Основной игровой цикл
def game_loop():
    global spaceship, bullets, resource_craters, obstacle_craters, score, collected_planets, start_time, missed_craters

    # Инициализация объектов
    spaceship = Spaceship()
    bullets = []
    resource_craters = [ResourceCrater() for _ in range(5)]
    obstacle_craters = [ObstacleCrater() for _ in range(5)]
    score = 0
    collected_planets = 0
    start_time = pygame.time.get_ticks()
    missed_craters = 0
    total_time = 60  # Общее время в секундах

    running = True
    clock = pygame.time.Clock()

    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_SPACE and spaceship.reload_timer == 0:
                    bullets.append(Bullet(spaceship.x + 20, spaceship.y))
                    shoot_sound.play()
                    spaceship.reload_timer = spaceship.reload_time

        keys = pygame.key.get_pressed()
        if keys[pygame.K_a]:
            spaceship.move_left()
        if keys[pygame.K_d]:
            spaceship.move_right()
        if keys[pygame.K_w]:
            spaceship.move_up()
        if keys[pygame.K_s]:
            spaceship.move_down()

        spaceship.reload()

        # Обновление пуль
        for bullet in bullets:
            bullet.move()
            if bullet.y < 0:
                if bullet in bullets:  # Проверка перед удалением
                    bullets.remove(bullet)

        # Обновление кратеров с ресурсами
        for crater in resource_craters:
            crater.move()
            if crater.y > HEIGHT:
                missed_craters += 1
                crater.reset()
            if spaceship.x < crater.x + 50 and spaceship.x + 50 > crater.x and spaceship.y < crater.y + 50 and spaceship.y + 50 > crater.y:
                collected_planets += 1
                resource_collision_sound.play()
                crater.reset()

        # Обновление кратеров-препятствий
        for crater in obstacle_craters:
            crater.move()
            if crater.y > HEIGHT:
                missed_craters += 1
                crater.reset()
            if spaceship.x < crater.x + 50 and spaceship.x + 50 > crater.x and spaceship.y < crater.y + 50 and spaceship.y + 50 > crater.y:
                spaceship.lives -= 1
                if spaceship.lives == 0:
                    game_over_sound.play()
                    running = False
                else:
                    spaceship.cry()
                obstacle_collision_sound.play()
                crater.reset()

        # Проверка столкновений пуль с кратерами
        for bullet in bullets:
            for crater in resource_craters:
                if bullet.x < crater.x + 50 and bullet.x + 10 > crater.x and bullet.y < crater.y + 50 and bullet.y + 10 > crater.y:
                    if bullet in bullets:  # Проверка перед удалением
                        bullets.remove(bullet)
                    crater.hits += 1
                    if crater.hits >= 2:
                        crater.exploding = True
                        resource_craters.remove(crater)
                        resource_craters.append(ResourceCrater())
                        score -= 10  # Снятие очков при поражении планет с ресурсами
                        explosion_sound.play()

            for crater in obstacle_craters:
                if bullet.x < crater.x + 50 and bullet.x + 10 > crater.x and bullet.y < crater.y + 50 and bullet.y + 10 > crater.y:
                    if bullet in bullets:  # Проверка перед удалением
                        bullets.remove(bullet)
                    crater.hits += 1
                    if crater.hits >= 3:
                        crater.exploding = True
                        obstacle_craters.remove(crater)
                        obstacle_craters.append(ObstacleCrater())
                        score += 10  # Добавление очков при поражении планет-препятствий
                        explosion_sound.play()

        # Проверка условий проигрыша
        if missed_craters >= 10 or spaceship.lives == 0 or (pygame.time.get_ticks() - start_time) / 1000 > total_time:
            game_over_sound.play()
            running = False

        # Проверка условия выигрыша
        if collected_planets >= 24:
            win_sound.play()
            running = False

        # Отрисовка градиентного фона
        for y in range(HEIGHT):
            color = (77 + y // 4, 49 + y // 4, 74 + y // 4)
            pygame.draw.line(screen, color, (0, y), (WIDTH, y))

        # Отрисовка объектов
        spaceship.draw()
        for bullet in bullets:
            bullet.draw()
        for crater in resource_craters:
            crater.draw()
        for crater in obstacle_craters:
            crater.draw()

        # Отображение жизней
        for i in range(spaceship.lives):
            screen.blit(heart_img, (10 + i * 40, 10))

        # Отображение информации
        text_score = font.render(f"Score: {score}", True, STARS)
        remaining_time = total_time - (pygame.time.get_ticks() - start_time) / 1000
        text_time = font.render(f"Time: {int(remaining_time)}s", True, STARS)
        text_planets = font.render(f"Planets: {collected_planets}/24", True, STARS)
        screen.blit(text_score, (10, 60))
        screen.blit(text_time, (10, 100))
        screen.blit(text_planets, (10, 140))

        # Отображение подсказок
        text_controls = font.render("Controls: W, A, S, D, Space to shoot", True, STARS)
        screen.blit(text_controls, (WIDTH - 350, 10))

        pygame.display.flip()
        clock.tick(30)

    # Отображение результата
    if collected_planets >= 24:
        pygame.mixer.music.stop()  # Остановка основной мелодии игры
        gif_index = 0
        while gif_index < len(win_gif):
            screen.fill((0, 0, 0))  # Заполнение экрана черным цветом
            gif_rect = win_gif[gif_index].get_rect(center=(WIDTH // 2, HEIGHT // 2))
            screen.blit(win_gif[gif_index], gif_rect)
            pygame.display.flip()
            pygame.time.wait(100)
            gif_index += 1
        while pygame.mixer.music.get_busy():
            pygame.time.wait(100)
    else:
        pygame.mixer.music.stop()  # Остановка основной мелодии игры
        gif_index = 0
        while gif_index < len(lose_gif):
            screen.fill((0, 0, 0))  # Заполнение экрана черным цветом
            gif_rect = lose_gif[gif_index].get_rect(center=(WIDTH // 2, HEIGHT // 2))
            screen.blit(lose_gif[gif_index], gif_rect)
            pygame.display.flip()
            pygame.time.wait(100)
            gif_index += 1
        while pygame.mixer.music.get_busy():
            pygame.time.wait(100)

    # Сохранение результатов
    save_results(score, collected_planets)

    # Отображение статистики
    screen.fill((0, 0, 0))  # Заполнение экрана черным цветом
    text_final_score = font.render(f"Final Score: {score}", True, STARS)
    text_final_planets = font.render(f"Collected Planets: {collected_planets}/24", True, STARS)
    screen.blit(text_final_score, (WIDTH // 2 - text_final_score.get_width() // 2, HEIGHT // 2 - 50))
    screen.blit(text_final_planets, (WIDTH // 2 - text_final_planets.get_width() // 2, HEIGHT // 2 + 50))
    pygame.display.flip()

    pygame.time.wait(5000)

    # Возврат в главное меню
    main_menu()

# Запуск главного меню
main_menu()
