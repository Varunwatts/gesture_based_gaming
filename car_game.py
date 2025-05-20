import pygame
import cv2
from gesture_control import HandDetector
import threading
import random
import os

# Gesture Detection Setup
detector = HandDetector()
gesture = "center"

def webcam_thread():
    global gesture
    cap = cv2.VideoCapture(0)
    while True:
        ret, frame = cap.read()
        frame = cv2.flip(frame, 1)
        frame, gesture = detector.detect_hand(frame)
        cv2.imshow("Gesture Control", frame)
        if cv2.waitKey(1) == 27:  # ESC to exit
            break
    cap.release()
    cv2.destroyAllWindows()

t = threading.Thread(target=webcam_thread)
t.daemon = True
t.start()

# Game Setup
pygame.init()
pygame.mixer.init()

WIDTH, HEIGHT = 500, 700
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Gesture-Controlled Car Game")

# Load Assets
ASSETS = "assets"
car_img = pygame.transform.scale(pygame.image.load(os.path.join(ASSETS, "car.png")), (50, 100))
enemy_img = pygame.transform.scale(pygame.image.load(os.path.join(ASSETS, "enemy_car.png")), (50, 100))
crash_sound = pygame.mixer.Sound(os.path.join(ASSETS, "crash.wav"))

# Lanes - evenly divided (3 lanes)
LANE_WIDTH = 80
ROAD_LEFT = WIDTH // 2 - LANE_WIDTH * 1.5
LANES = [ROAD_LEFT + i * LANE_WIDTH for i in range(3)]
lane_index = 1  # Start in center lane

# Show Start Screen
def show_start_screen():
    bg = pygame.image.load(os.path.join(ASSETS, "start_screen.png"))
    bg = pygame.transform.scale(bg, (WIDTH, HEIGHT))
    screen.blit(bg, (0, 0))

    title_font = pygame.font.SysFont("Arial", 36, bold=True)
    instruction_font = pygame.font.SysFont("Arial", 24)

    title = title_font.render("NEW GAME", True, (255, 255, 255))
    instruction = instruction_font.render("Press SPACE to Start", True, (255, 255, 255))

    screen.blit(title, (WIDTH//2 - title.get_width()//2, HEIGHT//2 - 100))
    screen.blit(instruction, (WIDTH//2 - instruction.get_width()//2, HEIGHT//2))
    pygame.display.update()

    waiting = True
    while waiting:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                exit()
            if event.type == pygame.KEYDOWN and event.key == pygame.K_SPACE:
                waiting = False

# Show Game Over Screen
def show_game_over_screen():
    screen.fill((0, 0, 0))
    font_big = pygame.font.SysFont("Arial", 48, bold=True)
    font_small = pygame.font.SysFont("Arial", 30)

    game_over_text = font_big.render("GAME OVER", True, (255, 0, 0))
    restart_text = font_small.render("Press R to Restart or ESC to Exit", True, (255, 255, 255))

    screen.blit(game_over_text, (WIDTH // 2 - game_over_text.get_width() // 2, HEIGHT // 2 - 100))
    screen.blit(restart_text, (WIDTH // 2 - restart_text.get_width() // 2, HEIGHT // 2))

    pygame.display.update()

    waiting = True
    while waiting:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                exit()
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_r:
                    waiting = False
                if event.key == pygame.K_ESCAPE:
                    pygame.quit()
                    exit()

# Initial Start Screen
show_start_screen()

# Game Variables
car_y = HEIGHT - 120
score = 0
font = pygame.font.SysFont("Arial", 30)

enemy_speed = 7
enemies = []
enemy_spawn_timer = 0
enemy_spawn_delay = 50

# Main Loop
clock = pygame.time.Clock()
running = True

while True:
    while running:
        screen.fill((50, 50, 50))
        pygame.draw.rect(screen, (80, 80, 80), (ROAD_LEFT, 0, LANE_WIDTH * 3, HEIGHT))

        # Draw lane dividers
        for i in range(1, 3):
            pygame.draw.line(screen, (255, 255, 255), (ROAD_LEFT + i * LANE_WIDTH, 0), (ROAD_LEFT + i * LANE_WIDTH, HEIGHT), 2)

        score_text = font.render(f"Score: {score}", True, (255, 255, 255))
        screen.blit(score_text, (10, 10))

        car_x = LANES[lane_index]
        screen.blit(car_img, (car_x, car_y))

        if gesture == "left" and lane_index > 0:
            lane_index -= 1
        elif gesture == "right" and lane_index < len(LANES) - 1:
            lane_index += 1

        enemy_spawn_timer += 1
        if enemy_spawn_timer >= enemy_spawn_delay:
            enemy_lane = random.choice(LANES)
            enemies.append(pygame.Rect(enemy_lane, -100, 50, 100))
            enemy_spawn_timer = 0

        player_rect = pygame.Rect(car_x, car_y, 50, 100)
        for enemy in enemies[:]:
            enemy.y += enemy_speed
            screen.blit(enemy_img, (enemy.x, enemy.y))
            if enemy.colliderect(player_rect):
                crash_sound.play()
                pygame.time.delay(1000)
                running = False

            if enemy.y > HEIGHT:
                enemies.remove(enemy)
                score += 1
                if score % 10 == 0:
                    enemy_speed += 1

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                exit()

        pygame.display.update()
        clock.tick(30)

    show_game_over_screen()

    # Reset Game State
    lane_index = 1
    car_y = HEIGHT - 120
    score = 0
    enemy_speed = 7
    enemies = []
    enemy_spawn_timer = 0
    running = True
