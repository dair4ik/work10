import pygame
import random
import psycopg2


conn = psycopg2.connect(
    dbname="neondb",
    user="neondb_owner",
    password="npg_nweOQjR2ryC3",
    host="ep-still-thunder-a54pyfes-pooler.us-east-2.aws.neon.tech",
    sslmode="require"
)
cursor = conn.cursor()

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


username = input("Enter your username: ").strip()
cursor.execute("INSERT INTO \"user\" (username) VALUES (%s) ON CONFLICT (username) DO NOTHING", (username,))
conn.commit()
cursor.execute("SELECT id FROM \"user\" WHERE username = %s", (username,))
user_id = cursor.fetchone()[0]


cursor.execute("""
    SELECT score, level FROM user_score
    WHERE user_id = %s
    ORDER BY id DESC LIMIT 1
""", (user_id,))
last_data = cursor.fetchone()
if last_data:
    score, level = last_data
else:
    score, level = 0, 1


LEVELS = {
    1: {"speed": 10, "walls": []},
    2: {"speed": 14, "walls": [(250, 150, 100, 20)]},
    3: {"speed": 17, "walls": [(200, 100, 20, 150), (380, 100, 20, 150)]},
    4: {"speed": 20, "walls": [(100, 150, 400, 20), (280, 50, 20, 100)]},
    5: {"speed": 23, "walls": [(100, 50, 400, 20), (100, 330, 400, 20), (290, 120, 20, 160)]},
}
MAX_LEVEL = max(LEVELS.keys())


pygame.init()
SCREEN_WIDTH = 600
SCREEN_HEIGHT = 400
CELL_SIZE = 20

WHITE = (255, 255, 255)
GREEN = (0, 255, 0)
RED = (255, 0, 0)
BLACK = (0, 0, 0)

background = pygame.image.load("backg.jpg")
background = pygame.transform.scale(background, (SCREEN_WIDTH, SCREEN_HEIGHT))
apple_img = pygame.image.load("apple1.png")
apple_img = pygame.transform.scale(apple_img, (CELL_SIZE, CELL_SIZE))

screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption("Snake Game(by Kaliyev Dair)")
font = pygame.font.SysFont("Verdana", 20)

snake = [(100, 100), (80, 100), (60, 100)]
snake_dir = (CELL_SIZE, 0)
paused = False


class Food:
    def __init__(self, walls):
        self.walls = walls
        self.respawn()

    def respawn(self):
        while True:
            self.x = random.randint(0, (SCREEN_WIDTH // CELL_SIZE) - 1) * CELL_SIZE
            self.y = random.randint(0, (SCREEN_HEIGHT // CELL_SIZE) - 1) * CELL_SIZE
            self.weight = random.randint(1, 3)
            self.timer = random.randint(50, 100)
            food_rect = pygame.Rect(self.x, self.y, CELL_SIZE, CELL_SIZE)
            if all(not pygame.Rect(wall).colliderect(food_rect) for wall in self.walls):
                break

    def update(self):
        self.timer -= 1
        if self.timer <= 0:
            self.respawn()

food = Food(LEVELS[level]["walls"])
running = True
clock = pygame.time.Clock()


while running:
    screen.blit(background, (0, 0))

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

        elif event.type == pygame.KEYDOWN:
            if event.key == pygame.K_p:
                paused = not paused
                if paused:
                
                    cursor.execute("""
                        SELECT score FROM user_score
                        WHERE user_id = %s
                        ORDER BY score DESC LIMIT 1
                    """, (user_id,))
                    row = cursor.fetchone()
                    if row is None or score > row[0]:
                        cursor.execute("""
                            INSERT INTO user_score (user_id, score, level) VALUES (%s, %s, %s)
                        """, (user_id, score, level))
                        conn.commit()

            if not paused:
                if event.key == pygame.K_UP and snake_dir != (0, CELL_SIZE):
                    snake_dir = (0, -CELL_SIZE)
                elif event.key == pygame.K_DOWN and snake_dir != (0, -CELL_SIZE):
                    snake_dir = (0, CELL_SIZE)
                elif event.key == pygame.K_LEFT and snake_dir != (CELL_SIZE, 0):
                    snake_dir = (-CELL_SIZE, 0)
                elif event.key == pygame.K_RIGHT and snake_dir != (-CELL_SIZE, 0):
                    snake_dir = (CELL_SIZE, 0)

    if paused:
        pause_text = font.render("PAUSED (Press P to Resume)", True, RED)
        screen.blit(pause_text, (SCREEN_WIDTH // 2 - 120, SCREEN_HEIGHT // 2))
        pygame.display.update()
        clock.tick(5)
        continue

    level_data = LEVELS.get(level, LEVELS[MAX_LEVEL])
    FPS = level_data["speed"]
    walls = level_data["walls"]

    new_head = (snake[0][0] + snake_dir[0], snake[0][1] + snake_dir[1])
    head_rect = pygame.Rect(new_head[0], new_head[1], CELL_SIZE, CELL_SIZE)

    if new_head[0] < 0 or new_head[0] >= SCREEN_WIDTH or new_head[1] < 0 or new_head[1] >= SCREEN_HEIGHT:
        running = False
    if new_head in snake:
        running = False
    for wall in walls:
        if pygame.Rect(wall).colliderect(head_rect):
            running = False

    snake.insert(0, new_head)

    if new_head == (food.x, food.y):
        score += food.weight
        if score > 0 and score % 5 == 0 and level < MAX_LEVEL:
            level += 1
            food = Food(LEVELS[level]["walls"])
        food.respawn()
    else:
        snake.pop()

    food.update()

    for segment in snake:
        pygame.draw.rect(screen, GREEN, (segment[0], segment[1], CELL_SIZE, CELL_SIZE))

    screen.blit(apple_img, (food.x, food.y))

    for wall in walls:
        pygame.draw.rect(screen, RED, wall)

    screen.blit(font.render(f"Score: {score}", True, WHITE), (10, 10))
    screen.blit(font.render(f"Level: {level}", True, WHITE), (10, 40))

    pygame.display.update()
    clock.tick(FPS)


cursor.execute("""
    SELECT score FROM user_score
    WHERE user_id = %s
    ORDER BY score DESC LIMIT 1
""", (user_id,))
row = cursor.fetchone()
if row is None or score > row[0]:
    cursor.execute("""
        INSERT INTO user_score (user_id, score, level) VALUES (%s, %s, %s)
    """, (user_id, score, level))
conn.commit()

cursor.close()
conn.close()
pygame.quit()
