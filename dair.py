import pygame
import random
import psycopg2

# ==== Подключение к базе данных ====
conn = psycopg2.connect(
    dbname="neondb",
    user="neondb_owner",
    password="npg_nweOQjR2ryC3",
    host="ep-still-thunder-a54pyfes-pooler.us-east-2.aws.neon.tech",
    sslmode="require"
)
cursor = conn.cursor()

# ==== Создание таблиц ====
cursor.execute("""
    CREATE TABLE IF NOT EXISTS "user" (
        id SERIAL PRIMARY KEY,
        username TEXT UNIQUE
    )
""")
cursor.execute("""
    CREATE TABLE IF NOT EXISTS user_score (
        id SERIAL PRIMARY KEY,
        user_id INTEGER REFERENCES "user"(id),
        score INTEGER,
        level INTEGER
    )
""")
conn.commit()

# ==== Ввод пользователя ====
pygame.init()
SCREEN_WIDTH = 600
SCREEN_HEIGHT = 400
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption("Snake Game - Menu")
font = pygame.font.SysFont("Verdana", 24)
small_font = pygame.font.SysFont("Verdana", 18)
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
GRAY = (100, 100, 100)
GREEN = (0, 255, 0)
RED = (255, 0, 0)

def draw_button(text, rect, color):
    pygame.draw.rect(screen, color, rect)
    label = small_font.render(text, True, BLACK)
    screen.blit(label, (rect[0] + 10, rect[1] + 10))

def get_user_input():
    username = ""
    input_box = pygame.Rect(150, 120, 300, 40)
    active = False
    while True:
        screen.fill(BLACK)
        label = font.render("Enter your username:", True, WHITE)
        screen.blit(label, (150, 70))
        txt_surface = font.render(username, True, WHITE)
        width = max(300, txt_surface.get_width()+10)
        input_box.w = width
        screen.blit(txt_surface, (input_box.x+5, input_box.y+5))
        pygame.draw.rect(screen, WHITE, input_box, 2)

        pygame.display.flip()
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                exit()
            elif event.type == pygame.MOUSEBUTTONDOWN:
                if input_box.collidepoint(event.pos):
                    active = True
            elif event.type == pygame.KEYDOWN:
                if active:
                    if event.key == pygame.K_RETURN:
                        return username.strip()
                    elif event.key == pygame.K_BACKSPACE:
                        username = username[:-1]
                    else:
                        username += event.unicode

username = get_user_input()

# ==== Проверка пользователя ====
cursor.execute("INSERT INTO \"user\" (username) VALUES (%s) ON CONFLICT (username) DO NOTHING", (username,))
conn.commit()
cursor.execute("SELECT id FROM \"user\" WHERE username = %s", (username,))
user_id = cursor.fetchone()[0]

# ==== Проверка существующего прогресса ====
cursor.execute("""
    SELECT score, level FROM user_score
    WHERE user_id = %s
    ORDER BY id DESC LIMIT 1
""", (user_id,))
last_data = cursor.fetchone()

def main_menu():
    while True:
        screen.fill(BLACK)
        screen.blit(font.render(f"Welcome, {username}", True, WHITE), (180, 50))
        if last_data:
            draw_button("Continue", pygame.Rect(200, 130, 200, 50), GREEN)
            draw_button("Restart", pygame.Rect(200, 200, 200, 50), RED)
        else:
            draw_button("Start Game", pygame.Rect(200, 160, 200, 50), GREEN)

        pygame.display.flip()
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                exit()
            elif event.type == pygame.MOUSEBUTTONDOWN:
                pos = event.pos
                if last_data:
                    if pygame.Rect(200, 130, 200, 50).collidepoint(pos):
                        return last_data[0], last_data[1]  # Continue
                    elif pygame.Rect(200, 200, 200, 50).collidepoint(pos):
                        return 0, 1  # Restart
                else:
                    if pygame.Rect(200, 160, 200, 50).collidepoint(pos):
                        return 0, 1  # Start new game

score, level = main_menu()

# === Основная часть игры ====
CELL_SIZE = 20
FPS = 10
WHITE = (255, 255, 255)
GREEN = (0, 255, 0)
RED = (255, 0, 0)
BLACK = (0, 0, 0)
SCREEN_WIDTH = 600
SCREEN_HEIGHT = 400
snake = [(100, 100), (80, 100), (60, 100)]
snake_dir = (CELL_SIZE, 0)

# Load apple image
apple_img = pygame.image.load("apple1.png")
apple_img = pygame.transform.scale(apple_img, (CELL_SIZE, CELL_SIZE))

# Load background image
background = pygame.image.load("backg.jpg")
background = pygame.transform.scale(background, (SCREEN_WIDTH, SCREEN_HEIGHT))

# Стены для каждого уровня
def generate_walls(level):
    walls = []
    num_walls = level * 2  # Увеличиваем количество стен с уровнем
    for _ in range(num_walls):
        x = random.randint(0, (SCREEN_WIDTH // CELL_SIZE) - 1) * CELL_SIZE
        y = random.randint(0, (SCREEN_HEIGHT // CELL_SIZE) - 1) * CELL_SIZE
        walls.append((x, y))
    return walls

walls = generate_walls(level)

# Food settings with random weight and timer
class Food:
    def __init__(self):
        self.respawn()

    def respawn(self):
        self.x = random.randint(0, (SCREEN_WIDTH // CELL_SIZE) - 1) * CELL_SIZE
        self.y = random.randint(0, (SCREEN_HEIGHT // CELL_SIZE) - 1) * CELL_SIZE
        self.weight = random.randint(1, 3)  # Food weight (1 to 3 points)
        self.timer = random.randint(50, 100)  # Timer before food disappears

    def update(self):
        self.timer -= 1
        if self.timer <= 0:
            self.respawn()

food = Food()

# Game variables
level = level
score = score
running = True
clock = pygame.time.Clock()

# Main game loop
while running:
    screen.blit(background, (0, 0))  # Draw background

    # Event handling
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

        elif event.type == pygame.KEYDOWN:
            if event.key == pygame.K_UP and snake_dir != (0, CELL_SIZE):
                snake_dir = (0, -CELL_SIZE)
            elif event.key == pygame.K_DOWN and snake_dir != (0, -CELL_SIZE):
                snake_dir = (0, CELL_SIZE)
            elif event.key == pygame.K_LEFT and snake_dir != (CELL_SIZE, 0):
                snake_dir = (-CELL_SIZE, 0)
            elif event.key == pygame.K_RIGHT and snake_dir != (-CELL_SIZE, 0):
                snake_dir = (CELL_SIZE, 0)

    # Move the snake
    new_head = (snake[0][0] + snake_dir[0], snake[0][1] + snake_dir[1])

    # Check for wall collision
    if new_head[0] < 0 or new_head[0] >= SCREEN_WIDTH or new_head[1] < 0 or new_head[1] >= SCREEN_HEIGHT:
        running = False  # Game over

    # Check if the snake collides with itself
    if new_head in snake:
        running = False  # Game over

    # Check if the snake collides with a wall
    if new_head in walls:
        running = False  # Game over

    # Add new head to snake
    snake.insert(0, new_head)

    # Check if food is eaten
    if new_head == (food.x, food.y):
        score += food.weight
        food.respawn()
    else:
        snake.pop()

    # Update food timer
    food.update()

    # Level up every 5 points
    if score % 5 == 0 and score > 0:
        level = score // 5 + 1
        FPS = 10 + (level * 2)
        walls = generate_walls(level)  # Генерируем новые стены при повышении уровня

    # Draw snake
    for segment in snake:
        pygame.draw.rect(screen, GREEN, (segment[0], segment[1], CELL_SIZE, CELL_SIZE))

    # Draw apple (food)
    screen.blit(apple_img, (food.x, food.y))

    # Draw walls
    for wall in walls:
        pygame.draw.rect(screen, RED, (wall[0], wall[1], CELL_SIZE, CELL_SIZE))

    # Display score and level
    score_text = font.render(f"Score: {score}", True, WHITE)
    level_text = font.render(f"Level: {level}", True, WHITE)
    screen.blit(score_text, (10, 10))
    screen.blit(level_text, (10, 40))

    # Update screen
    pygame.display.update()
    clock.tick(FPS)  # Control game speed

# Quit pygame
pygame.quit()

# === Сохранение результата ====
cursor.execute("""
    INSERT INTO user_score (user_id, score, level) 
    VALUES (%s, %s, %s)
""", (user_id, score, level))
conn.commit()

conn.close()
