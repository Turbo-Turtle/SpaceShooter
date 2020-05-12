import pygame
import os
import time
import random
pygame.font.init()
# frequency, size, channels, buffersize
pygame.mixer.pre_init(44100, 16, 2, 4096)
pygame.init()

WIDTH, HEIGHT = 750, 750
WIN = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("My Space Shooter")

# Load images
ENEMY_SCOUT_SHIP = pygame.image.load(
    os.path.join("assets", "enemy_scout_ship.png"))
ENEMY_FIGHTER_SHIP = pygame.image.load(
    os.path.join("assets", "enemy_fighter_ship.png"))
ENEMY_ASSAULT_SHIP = pygame.image.load(
    os.path.join("assets", "enemy_assault_ship.png"))

# Player ship
PLAYER_SPACE_SHIP = pygame.image.load(
    os.path.join("assets", "player_ship.png"))

# Laser images
ENEMY_SCOUT_LASER = pygame.image.load(
    os.path.join("assets", "enemy_scout_laser.png"))
ENEMY_FIGHTER_LASER = pygame.image.load(
    os.path.join("assets", "enemy_fighter_laser.png"))
ENEMY_ASSAULT_LASER = pygame.image.load(
    os.path.join("assets", "enemy_assault_laser.png"))
PLAYER_LASER = pygame.image.load(
    os.path.join("assets", "player_laser.png"))

BG = pygame.transform.scale(pygame.image.load(
    os.path.join("assets", "atmosphere-background.png")), (WIDTH, HEIGHT))

INGAME_MUSIC = pygame.mixer.music.load("Music.mp3")
PLAYER_THRUST = pygame.mixer.Sound("Thrust.wav")

PLAYER_FIRE = pygame.mixer.Sound("Fire.wav")


#==============================================


class Laser:
    def __init__(self, x, y, img):
        self.x = x + 36
        self.y = y
        self.img = img
        self.mask = pygame.mask.from_surface(self.img)

    def draw(self, window):
        window.blit(self.img, (self.x, self.y))

    def move(self, vel):
        self.y += vel

    def off_screen(self, height):
        return not (self.y <= height and self.y >= 0)

    def collision(self, obj):
        return collide(self, obj)


#==========================

class Ship:
    COOLDOWN = 30

    def __init__(self, x, y, health=100):
        self.x = x
        self.y = y
        self.health = health
        self.ship_img = None
        self.laser_img = None
        self.lasers = []
        self.cool_down_counter = 0

    def draw(self, window):
        window.blit(self.ship_img, (self.x, self.y))
        for laser in self.lasers:
            laser.draw(window)

    def move_lasers(self, vel, obj):
        self.cooldown()
        for laser in self.lasers:
            laser.move(vel)
            if laser.off_screen(HEIGHT):
                self.lasers.remove(laser)
            elif laser.collision(obj):
                obj.health -= 10
                self.lasers.remove(laser)

    def cooldown(self):
        if self.cool_down_counter >= self.COOLDOWN:
            self.cool_down_counter = 0
        elif self.cool_down_counter > 0:
            self.cool_down_counter += 1

    def shoot(self):
        if self.cool_down_counter == 0:
            laser = Laser(self.x, self.y, self.laser_img)
            self.lasers.append(laser)
            self.cool_down_counter = 1

    def get_width(self):
        return self.ship_img.get_width()

    def get_height(self):
        return self.ship_img.get_height()

#=========================


class Player(Ship):
    def __init__(self, x, y, health=100):
        super().__init__(x, y, health)
        self.ship_img = PLAYER_SPACE_SHIP
        self.laser_img = PLAYER_LASER
        self.mask = pygame.mask.from_surface(self.ship_img)
        self.max_health = health

    def move_lasers(self, vel, objs):
        self.cooldown()
        for laser in self.lasers:
            laser.move(vel)
            if laser.off_screen(HEIGHT):
                self.lasers.remove(laser)
            else:
                for obj in objs:
                    if laser.collision(obj):
                        objs.remove(obj)
                        if laser in self.lasers:
                            self.lasers.remove(laser)

    def draw(self, window):
        super().draw(window)
        self.healthbar(window)

    def healthbar(self, window):
        pygame.draw.rect(window, (255, 0, 0), (self.x, self.y +
                                               self.ship_img.get_height() + 10, self.ship_img.get_width(), 10))
        pygame.draw.rect(window, (0, 255, 0), (self.x, self.y + self.ship_img.get_height() +
                                               10, self.ship_img.get_width() * (self.health / self.max_health), 10))
#=========================


class Enemy(Ship):
    UNIT_MAP = {"scout": (ENEMY_SCOUT_SHIP, ENEMY_SCOUT_LASER), "fighter": (
        ENEMY_FIGHTER_SHIP, ENEMY_FIGHTER_LASER), "assault": (ENEMY_ASSAULT_SHIP, ENEMY_ASSAULT_LASER)}

    def __init__(self, x, y, unit, health=100):
        super().__init__(x, y, health)
        self.ship_img, self.laser_img = self.UNIT_MAP[unit]
        self.mask = pygame.mask.from_surface(self.ship_img)

    def move(self, vel):
        self.y += vel

    def shoot(self):
        if self.cool_down_counter == 0:
            laser = Laser(self.x - 28, self.y + 30, self.laser_img)
            self.lasers.append(laser)
            self.cool_down_counter = 1

#==============================================


def collide(obj1, obj2):
    offset_x = obj2.x - obj1.x
    offset_y = obj2.y - obj1.y
    return obj1.mask.overlap(obj2.mask, (offset_x, offset_y)) != None


def main():
    run = True
    FPS = 60
    level = 0
    lives = 5
    player_vel = 5
    laser_vel = 4
    main_font = pygame.font.SysFont("comicsans", 50)
    lost_font = pygame.font.SysFont("comicsans", 70)

    enemies = []
    wave_length = 5
    enemy_vel = 1

    player = Player(300, 620)

    pygame.mixer.music.play(-1)

    clock = pygame.time.Clock()

    lost = False
    lost_count = 0

    def redraw_window():
        WIN.blit(BG, (0, 0))

        lives_label = main_font.render(f"Lives: {lives}", 1, (255, 255, 255))
        level_label = main_font.render(f"Level: {level}", 1, (145, 0, 0))

        WIN.blit(lives_label, (10, 10))
        WIN.blit(level_label, (WIDTH - level_label.get_width() - 10, 10))

        for enemy in enemies:
            enemy.draw(WIN)

        player.draw(WIN)

        if lost:
            lost_label = lost_font.render("You Lost!!", 1, (255, 255, 255))
            WIN.blit(lost_label, (WIDTH / 2 - lost_label.get_width() / 2, 350))
            pygame.mixer.music.fadeout(1600)

        pygame.display.update()

    while run:
        clock.tick(FPS)
        redraw_window()

        if lives <= 0 or player.health <= 0:
            lost = True
            lost_count += 1

        if lost:
            if lost_count > FPS * 3:
                run = False
            else:
                continue

        if len(enemies) == 0:
            level += 1
            wave_length += 5
            for i in range(wave_length):
                enemy = Enemy(random.randrange(
                    50, WIDTH - 100), random.randrange(-1500, -100), random.choice(["scout", "fighter", "assault"]))
                enemies.append(enemy)

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                quit()

        keys = pygame.key.get_pressed()
        if keys[pygame.K_a] and player.x - player_vel + 40 > 0:  # left

            player.x -= player_vel
        if keys[pygame.K_d] and player.x + player_vel + player.get_width() - 40 < WIDTH:  # Right
            player.x += player_vel
        if keys[pygame.K_w] and player.y - player_vel > 0:  # Up
            player.y -= player_vel
        if keys[pygame.K_s] and player.y + player_vel + player.get_height() - 40 < HEIGHT:  # Down
            player.y += player_vel
        if keys[pygame.K_SPACE]:
            pygame.mixer.Sound.play(PLAYER_FIRE)
            player.shoot()

        for enemy in enemies[:]:
            enemy.move(enemy_vel)
            enemy.move_lasers(laser_vel, player)

            if random.randrange(0, 3 * 60) == 1:
                enemy.shoot()

            if collide(enemy, player):
                player.health -= 10
                enemies.remove(enemy)
            elif enemy.y + enemy.get_height() > HEIGHT:
                lives -= 1
                enemies.remove(enemy)

        player.move_lasers(-laser_vel, enemies)


def main_menu():
    title_font = pygame.font.SysFont("comicsans", 70)
    run = True
    while run:
        WIN.blit(BG, (0, 0))
        title_label = title_font.render(
            "Press the mouse to begin...", 1, (255, 255, 255))
        WIN.blit(title_label, (WIDTH / 2 - title_label.get_width() / 2, 350))
        pygame.display.update()
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                run = False
            if event.type == pygame.MOUSEBUTTONDOWN:
                main()

    pygame.quit()


main_menu()
# Tutorial video time marker @ 1:07:00
