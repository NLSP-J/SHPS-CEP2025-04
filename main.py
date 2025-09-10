import pygame as pg
import random
import asyncio

pg.init()
clock = pg.time.Clock()

# Colors
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
GREEN = (0, 255, 0)
RED = (255, 0, 0)

# Window size
WIDTH, HEIGHT = 800, 600
screen = pg.display.set_mode((WIDTH, HEIGHT))
pg.display.set_caption('Minecraft: Game Modes')

font = pg.font.Font(None, 30)
big_font = pg.font.Font(None, 60)

mode = 'menu'

# Load images
try:
    player_img = pg.transform.scale(pg.image.load('./assets/images/big-steve-face.jpg'), (40, 40))
    zombie_img = pg.transform.scale(pg.image.load('./assets/images/Minecraft-Zombie-Head.jpg'), (60, 60))
    bg_img = pg.transform.scale(pg.image.load('./assets/images/mountain.png'), (WIDTH, HEIGHT))
except Exception as e:
    print("Error loading images. Make sure the image files exist.")
    print(e)
    pg.quit()

MAX_LEVEL = 20


def reset_game():
    return {
        "level": 1,
        "score": 0,
        "health": 30,  
        "speed": 5,
        "player_pos": [WIDTH / 2, HEIGHT - 40],
        "zombies": [],
        "level_up_timer": 0,
        "health_timer": pg.time.get_ticks()
    }

state = reset_game()


def show_menu():
    global mode, state

    screen.fill(WHITE)
    title = big_font.render("Minecraft: Game Modes", True, BLACK)
    mode1 = font.render("Press 1 - Falling Zombies", True, GREEN)
    mode2 = font.render("Press 2 - Climb to the Top", True, RED)
    screen.blit(title, (WIDTH // 2 - title.get_width() // 2, 180))
    screen.blit(mode1, (WIDTH // 2 - mode1.get_width() // 2, 270))
    screen.blit(mode2, (WIDTH // 2 - mode2.get_width() // 2, 320))

    for event in pg.event.get():
        if event.type == pg.QUIT:
            pg.quit()
        if event.type == pg.KEYDOWN:
            if event.key == pg.K_1:
                mode = 'fall'
                state = reset_game()
            elif event.key == pg.K_2:
                mode = 'climb'
                state = reset_game()


def show_message(text, color):
    screen.fill(WHITE)
    msg = big_font.render(text, True, color)
    sub = font.render("Press ESC to return to menu", True, BLACK)
    screen.blit(msg, (WIDTH // 2 - msg.get_width() // 2, HEIGHT // 2 - 30))
    screen.blit(sub, (WIDTH // 2 - sub.get_width() // 2, HEIGHT // 2 + 40))


def falling_zombies_mode():
    global mode, state
    # Event handling
    for event in pg.event.get():
        if event.type == pg.QUIT:
            pg.quit()
        if event.type == pg.KEYDOWN:
            if event.key == pg.K_ESCAPE:
                mode = 'menu'
            x, y = state["player_pos"]
            if event.key == pg.K_LEFT and x > 0:
                x -= 40
            if event.key == pg.K_RIGHT and x < WIDTH - 40:
                x += 40
            state["player_pos"] = [x, y]

    # Health regen every 5 seconds
    if pg.time.get_ticks() - state["health_timer"] > 5000:
        if state["health"] < 30:
            state["health"] += 1
        state["health_timer"] = pg.time.get_ticks()

    # Update level and speed based on score
    new_level = min(state["score"] // 25 + 1, MAX_LEVEL)
    if new_level > state["level"]:
        state["level"] = new_level
        state["level_up_timer"] = pg.time.get_ticks()
        state["speed"] = 5 + state["level"] // 2

    # Spawn zombies with improved chance
    spawn_chance = 0.15 + (state["level"] * 0.04)
    if len(state["zombies"]) < 10 and random.random() < spawn_chance:
        x = random.randint(0, WIDTH - 60)
        state["zombies"].append([x, 0])

    # Draw background first!
    screen.blit(bg_img, (0, 0))

    # Update and draw zombies
    for z in state["zombies"][:]:
        z[1] += state["speed"]
        screen.blit(zombie_img, (z[0], z[1]))
        if z[1] > HEIGHT:
            state["zombies"].remove(z)
            state["score"] += 1

    # Draw player last so it appears on top
    screen.blit(player_img, state["player_pos"])

    # Check collisions
    px, py = state["player_pos"]
    player_rect = pg.Rect(px, py, 40, 40)
    for z in state["zombies"][:]:
        zx, zy = z
        zombie_rect = pg.Rect(zx, zy, 60, 60)
        if player_rect.colliderect(zombie_rect):
            state["zombies"].remove(z)
            state["health"] -= 1
            if state["health"] <= 0:
                show_message("Game Over!", RED)
                mode = 'message'

    # Draw UI
    status = font.render(f'Score: {state["score"]}  Health: {state["health"]}  Level: {state["level"]}', True, BLACK)
    screen.blit(status, (10, HEIGHT - 30))

    # Level up message for 2 seconds
    if state["level_up_timer"] and pg.time.get_ticks() - state["level_up_timer"] < 2000:
        level_text = font.render(f'Level Up! Level {state["level"]}', True, RED)
        screen.blit(level_text, (WIDTH // 2 - 80, HEIGHT // 2 - 60))
    else:
        state["level_up_timer"] = 0

    # Win condition
    if state["level"] >= MAX_LEVEL:
        show_message("You Win!", GREEN)
        mode = 'message'


def climb_mode():
    global mode, state
    # Event handling
    for event in pg.event.get():
        if event.type == pg.QUIT:
            pg.quit()
        if event.type == pg.KEYDOWN:
            if event.key == pg.K_ESCAPE:
                mode = 'menu'
            x, y = state["player_pos"]
            if event.key == pg.K_LEFT and x > 0:
                x -= 40
            if event.key == pg.K_RIGHT and x < WIDTH - 40:
                x += 40
            if event.key == pg.K_UP and y > 0:
                y -= 4
            if event.key == pg.K_DOWN and y < HEIGHT - 40:
                y += 40
            state["player_pos"] = [x, y]

    # Spawn zombies falling (NO health regen here)
    spawn_chance = 0.15 + (state["level"] * 0.04)
    if len(state["zombies"]) < 10 and random.random() < spawn_chance:
        x = random.randint(0, WIDTH - 60)
        state["zombies"].append([x, 0])

    # Draw background first
    screen.blit(bg_img, (0, 0))

    # Update and draw zombies
    for z in state["zombies"][:]:
        z[1] += state["speed"]
        screen.blit(zombie_img, (z[0], z[1]))
        if z[1] > HEIGHT:
            state["zombies"].remove(z)

    # Draw player last so it is visible on top
    screen.blit(player_img, state["player_pos"])

    # Collision check
    px, py = state["player_pos"]
    player_rect = pg.Rect(px, py, 40, 40)
    for z in state["zombies"][:]:
        zx, zy = z
        zombie_rect = pg.Rect(zx, zy, 60, 60)
        if player_rect.colliderect(zombie_rect):
            state["zombies"].remove(z)
            state["health"] -= 1
            if state["health"] <= 0:
                show_message("Game Over!", RED)
                return

    # Win condition: reach top
    if py <= 0:
        state["level"] += 1
        if state["level"] > MAX_LEVEL:
            show_message("You Win!", GREEN)
            mode = 'message'

        # Full health replenish every 5 levels
        if state["level"] % 5 == 0:
            state["health"] = 30

        # Increase difficulty
        state["speed"] = 5 + state["level"] // 2

        # Reset player and zombies for next level
        state["player_pos"] = [WIDTH // 2, HEIGHT - 40]
        state["zombies"] = []

        # Show level up message timer
        state["level_up_timer"] = pg.time.get_ticks()

    # Draw UI
    status = font.render(f'Health: {state["health"]}  Level: {state["level"]}', True, BLACK)
    screen.blit(status, (10, HEIGHT - 30))

    # Level up message for 2 seconds
    if state["level_up_timer"] and pg.time.get_ticks() - state["level_up_timer"] < 2000:
        level_text = font.render(f'Level Up! Level {state["level"]}', True, RED)
        screen.blit(level_text, (WIDTH // 2 - 80, HEIGHT // 2 - 60))
    else:
        state["level_up_timer"] = 0



async def main():
    global mode
    while True:
        if mode == 'menu':
            show_menu()
        elif mode == 'fall':
            falling_zombies_mode()
        elif mode == 'climb':
            climb_mode()
        elif mode == 'message':
            for event in pg.event.get():
                if event.type == pg.QUIT:
                    pg.quit()
                if event.type == pg.KEYDOWN and event.key == pg.K_ESCAPE:
                    mode = 'menu'

        clock.tick(60)
        pg.display.flip()

        await asyncio.sleep(0)

asyncio.run(main())