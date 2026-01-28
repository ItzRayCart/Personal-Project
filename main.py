import pygame
import random
import time
import math
import os
from pygame import mixer

# Initialize pygame and set up the display
pygame.init()
width, height = pygame.display.Info().current_w, pygame.display.Info().current_h
screen = pygame.display.set_mode((width, height), pygame.FULLSCREEN)
pygame.display.set_caption('Shooting Game')

# Define colors, initial score, and game over flag
RED, COLOUR, WHITE, BLACK, ORANGE = (255, 0, 0), (0, 0, 255), (255, 255, 255), (0, 0, 0), (255, 165, 0)
score, high_score = 0, 0

pygame.mixer.init()
shoot_sound = pygame.mixer.Sound("Pew Sound Effect.wav")
transform_sound = pygame.mixer.Sound('Transform.wav')
transform_sound.set_volume(2.0)
mixer.music.load('Background.wav')
mixer.music.play(-1)

# Define player, enemies, and bullets
player_size = 30
player = {'rect': pygame.Rect(width // 2 - int(player_size * 1.5) // 2, height - 50, int(player_size * 1.5),
                              int(player_size * 1.5)),
          'speed': 10, 'direction': 'right', 'boosted': False, 'boost_start_time': 0}
enemies = []
triangles = []
player_bullets = []
enemy_bullets = []

# Credits for game won screen
credits = [
    "Creator: Rayyan Ahmad Raza",
    "Creative Designer: Rayyan Ahmad Raza",
    "Programmer: Rayyan Ahmad Raza"
]

# Bullet Speed
bullet_speed = 5
# Boost settings
boost_duration = 10  # seconds
boost_cooldown = 10  # seconds
boost_cooldown_start_time = 0

#triangle movement speed
speed_limit_a = 1
speed_limit_b = 2

# Enemy spawn rate
enemy_spawn_rate = 2  # Increase or decrease as needed
global total_enemies_triangles
total_enemies_triangles = 0
# Define font for score and game over display
font = pygame.font.Font(None, 36)

# Function to add triangles
def add_triangle():
    global total_enemies_triangles, speed_limit_a, speed_limit_b
    if total_enemies_triangles >= 10:
        return  # Stop spawning when the total count reaches 10
    triangle_size = 40
    triangle_x = random.randint(0, width - triangle_size)
    triangle_y = random.randint(0, height // 4 * 3 - triangle_size)
    # Ensure no two triangles spawn in the same row or near each other
    while any(abs(triangle_y - t['rect'].y) < triangle_size for t in triangles):
        triangle_y = random.randint(0, height // 4 * 3 - triangle_size)
    triangles.append({'rect': pygame.Rect(triangle_x, triangle_y, triangle_size, triangle_size),
                      'speed': random.uniform(speed_limit_a, speed_limit_b), 'direction': random.choice([-1, 1]),
                      'health': 2, 'start_time': time.time(), 'change_direction_time': random.uniform(2, 4)})
    total_enemies_triangles += 1



def add_square():
    global total_enemies_triangles
    if total_enemies_triangles >= 10:
        return  # Stop spawning when the total count reaches 10
    enemy_x = random.randint(0, width - 40)
    enemy_y = random.randint(0, height // 4 * 3 - 40)
    enemies.append({'rect': pygame.Rect(enemy_x, enemy_y, 40, 40), 'speed': random.randint(1, 3)})
    total_enemies_triangles += 1


# Modify the existing add_enemy function to handle squares and triangles
def add_enemy():
    global total_enemies_triangles
    if total_enemies_triangles >= 10:
        return  # Stop spawning when the total count reaches 10
    if random.choice([True, False]):  # Randomly choose between square and triangle
        add_square()
    else:
        add_triangle()

# Function to destroy a triangle and increase score
def destroy_triangle(triangle):
    score = 0
    high_score = 0
    triangles.remove(triangle)
    score += 1
    if score > high_score:
        high_score = score


def destroy_square(enemy):
    global total_enemies_triangles
    enemies.remove(enemy)
    total_enemies_triangles -= 1

# Function to draw text
def draw_text(surface, text, color, rect):
    text_surface = font.render(text, True, color)
    surface.blit(text_surface, rect)

# File path for storing high score
high_score_file_path = "high_score.txt"

# Function to save high score to a file
def save_high_score(score):
    with open(high_score_file_path, "w") as file:
        file.write(str(score))

# Function to load high score from a file
def load_high_score():
    if os.path.exists(high_score_file_path):
        with open(high_score_file_path, "r") as file:
            return int(file.read())
    else:
        return 0



def reset_game_state():
    global player, enemies, triangles, player_bullets, enemy_bullets, score, bullet_speed
    player = {'rect': pygame.Rect(width // 2 - int(player_size * 1.5) // 2, height - 50, int(player_size * 1.5),
                                  int(player_size * 1.5)),
              'speed': 10, 'direction': 'right', 'boosted': False, 'boost_start_time': 0}
    enemies = []
    bullet_speed = 5
    triangles = []
    player_bullets = []
    enemy_bullets = []
    score = 0
    COLOUR = (0,0,255)
    speed_limit_a = 1
    speed_limit_b = 2

# Function to handle game over
def game_over_screen():
    global total_enemies_triangles, high_score  # Add this line to access the global variable
    screen.fill(BLACK)
    draw_text(screen, 'GAME OVER', WHITE, (width // 2 - 100, height // 2 - 50))
    draw_text(screen, 'Score: ' + str(score), WHITE, (width // 2 - 100, height // 2))
    draw_text(screen, 'High Score: ' + str(high_score), WHITE, (width // 2 - 100, height // 2 + 50))

    retry_button_rect = pygame.Rect(width // 2 - 100, height // 2 + 100, 200, 50)
    quit_button_rect = pygame.Rect(width // 2 - 100, height // 2 + 150, 200, 50)

    pygame.draw.rect(screen, BLACK, retry_button_rect)
    pygame.draw.rect(screen, BLACK, quit_button_rect)

    draw_text(screen, 'Retry', WHITE, retry_button_rect)
    draw_text(screen, 'Quit Game', WHITE, quit_button_rect)

    pygame.display.flip()

    waiting = True
    while waiting:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                return 'quit'
            if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                if retry_button_rect.collidepoint(event.pos):
                    waiting = False
                    total_enemies_triangles = 0  # Reset the total count on retry
                    return 'retry'
                elif quit_button_rect.collidepoint(event.pos):
                    waiting = False
                    return 'quit'
    return 'quit'


# Function to display start menu
def start_menu():
    global credits
    screen.fill(BLACK)
    draw_text(screen, 'Controls:', WHITE, (10, 10))
    draw_text(screen, 'A to Go Left', WHITE, (10, 50))
    draw_text(screen, 'D to Go Right', WHITE, (10, 90))
    draw_text(screen, 'Space to Shoot', WHITE, (10, 130))
    draw_text(screen, 'Shift for Super Mode (10s Duration, 10s Cooldown)', WHITE, (10, 170))
    draw_text(screen, 'Creator: Rayyan Ahmad Raza', WHITE, (width // 2 - 200, height // 2 + 125, 200, 50))
    start_button_rect = pygame.Rect(width // 2 - 100, height // 2 - 25, 200, 50)
    quit_button_rect = pygame.Rect(width // 2 - 130, height // 2 + 50, 200, 50)
    pygame.draw.rect(screen, BLACK, start_button_rect)
    pygame.draw.rect(screen, BLACK, quit_button_rect)
    draw_text(screen, 'Start', WHITE, start_button_rect)
    draw_text(screen, 'Quit Game', WHITE, quit_button_rect)
    pygame.display.flip()

    waiting = True
    while waiting:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                return True
            if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                if start_button_rect.collidepoint(event.pos):
                    waiting = False
                elif quit_button_rect.collidepoint(event.pos):
                    pygame.quit()
                    return True
    return False



# Generate initial star positions and speeds
num_stars = 100
stars = [{'pos': [random.randint(0, width), random.randint(0, height)], 'speed': random.uniform(1, 3)} for _ in
         range(num_stars)]

# Main game loop
running = True
pressed_keys = set()  # To keep track of currently pressed keys
high_score = load_high_score()

# Display start menu
if start_menu():
    pygame.quit()
    exit()
game_over = False
game_won = False
paused = False
while running:
    if game_over:
        action = game_over_screen()
        if action == 'quit':
            break
        elif action == 'retry':
            reset_game_state()
            COLOUR = (0,0,255)
        game_over = False


    current_time = time.time()

    # Update speed limits based on the score
    if score >= 0 and score < 100:
        speed_limit_a = 2
        speed_limit_b = 3
    elif score >= 100 and score < 200:
        speed_limit_a = 3
        speed_limit_b = 4
    elif score >= 200 and score < 300:
        speed_limit_a = 4
        speed_limit_b = 5
    elif score >= 300 and score < 400:
        speed_limit_a = 5
        speed_limit_b = 6
    elif score >= 400 and score < 500:
        speed_limit_a = 6
        speed_limit_b = 7



    # Event handling
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        elif event.type == pygame.KEYDOWN:
            pressed_keys.add(event.key)
            if event.key == pygame.K_SPACE:
                shoot_sound.play(maxtime=500)
                bullet_direction = player['direction']
                bullet_x = player['rect'].centerx - 2
                bullet_y = player['rect'].centery - 10
                player_bullets.append(pygame.Rect(bullet_x, bullet_y, 5, 20))
                if player['boosted']:
                    bullet_x_left = player['rect'].left - 2
                    bullet_x_right = player['rect'].right - 2
                    player_bullets.append(pygame.Rect(bullet_x_left, bullet_y, 5, 20))
                    player_bullets.append(pygame.Rect(bullet_x_right, bullet_y, 5, 20))

    if not paused:
        # Player movement
        dx = 0
        dy = 0

        # Check for key events
        keys = pygame.key.get_pressed()
        if keys[pygame.K_LEFT]:
            dx -= player['speed']
            player['direction'] = 'left'
        if keys[pygame.K_RIGHT]:
            dx += player['speed']
            player['direction'] = 'right'

        # Boost handling
        if keys[pygame.K_LSHIFT] or keys[pygame.K_RSHIFT]:
            if not player['boosted'] and current_time - boost_cooldown_start_time >= boost_cooldown:
                transform_sound.play()
                player['speed'] *= 1.5
                player['boosted'] = True
                player['boost_start_time'] = current_time

        player['rect'].move_ip(dx, dy)
        player['rect'].clamp_ip(screen.get_rect())

        # Update player bullets
        for bullet in player_bullets[:]:
            bullet.move_ip(0, -int(10 * 1.5))  # Increase bullet speed by 1.5 times
            if not screen.get_rect().contains(bullet):
                player_bullets.remove(bullet)

        # Update enemies
        if random.randint(1, 100) <= enemy_spawn_rate:  # Adjust spawn rate
            add_enemy()
        for enemy in enemies[:]:
            if enemy['rect'].colliderect(player['rect']):
                if not player['boosted']:
                    game_over = True
                break
            if random.randint(1, 100) == 1:  # Chance for enemy to shoot
                enemy_bullets.append(pygame.Rect(enemy['rect'].centerx - 2, enemy['rect'].centery, 5, 20))
            for bullet in player_bullets:
                if bullet.colliderect(enemy['rect']):
                    total_enemies_triangles -= 1
                    if player['boosted']:
                        score += 2  # Double the score during the boosted state
                        if score >= 0 and score < 100:
                            COLOUR = (0, 0, 255)
                        elif score >= 100 and score < 200:
                            COLOUR = (0, 255, 0)
                        elif score >= 200 and score < 300:
                            COLOUR = (128, 0, 128)
                        elif score >= 300:
                            COLOUR = (192, 192, 192)
                    else:
                        score += 1
                        if score >= 0 and score < 100:
                            COLOUR = (0, 0, 255)
                        elif score >= 100 and score < 200:
                            COLOUR = (0, 255, 0)
                        elif score >= 200 and score < 300:
                            COLOUR = (128, 0, 128)
                        elif score >= 300:
                            COLOUR = (192, 192, 192)
                    if score > high_score:
                        high_score = score
                        save_high_score(high_score)
                    enemies.remove(enemy)
                    player_bullets.remove(bullet)
                    break

        # Inside the main game loop, update the triangles' positions
        for triangle in triangles[:]:
            triangle['rect'].move_ip(triangle['speed'] * triangle['direction'], 0)
            triangle['rect'].clamp_ip(screen.get_rect())

            # Change direction and reset the time to change direction when reaching the screen edge
            if triangle['rect'].left <= 0 or triangle['rect'].right >= width:
                triangle['direction'] *= -1
                triangle['start_time'] = current_time

            # Change direction after 2 to 4 seconds
            if current_time - triangle['start_time'] > triangle['change_direction_time']:
                triangle['direction'] *= -1
                triangle['start_time'] = current_time

        # Update triangles and check for collisions with player bullets
        for triangle in triangles[:]:
            triangle['rect'].move_ip(triangle['speed'] * triangle['direction'], 0)
            triangle['rect'].clamp_ip(screen.get_rect())
            # Change direction after 2 to 4 seconds
            if current_time - triangle['start_time'] > triangle['change_direction_time']:
                triangle['direction'] *= -1
                triangle['start_time'] = current_time

            # Check for collisions with player bullets
            for bullet in player_bullets[:]:
                if bullet.colliderect(triangle['rect']):
                    triangle['health'] -= 1
                    player_bullets.remove(bullet)
                    if triangle['health'] == 0:
                        destroy_triangle(triangle)
                        total_enemies_triangles -= 1
                        if player['boosted']:
                            score += 4  # Double the score during the boosted state
                            if score >= 0 and score < 100:
                                COLOUR = (0, 0, 255)
                            elif score >= 100 and score < 200:
                                COLOUR = (0, 255, 0)
                            elif score >= 200 and score < 300:
                                COLOUR = (128, 0, 128)
                            elif score >= 300:
                                COLOUR = (192, 192, 192)
                        else:
                            score += 2
                            if score >= 0 and score < 100:
                                COLOUR = (0, 0, 255)
                            elif score >= 100 and score < 200:
                                COLOUR = (0, 255, 0)
                            elif score >= 200 and score < 300:
                                COLOUR = (128, 0, 128)
                            elif score >= 300:
                                COLOUR = (192, 192, 192)
                        if score > high_score:
                            high_score = score
                            save_high_score(high_score)

                    break

        # Let triangles shoot
        for triangle in triangles:
            if random.randint(1, 100) == 1:  # Adjust the chance for triangles to shoot
                enemy_bullets.append(pygame.Rect(triangle['rect'].centerx - 2, triangle['rect'].centery, 5, 20))

        # Update enemy bullets
        for bullet in enemy_bullets[:]:
            bullet_speed = int(5 + (score // 100) * 3)  # Increase enemy bullet speed by 3 for every 100 points
            bullet.move_ip(0, bullet_speed)
            if player['rect'].colliderect(bullet) and not player['boosted']:
                game_over = True
                break
            if not screen.get_rect().contains(bullet):
                enemy_bullets.remove(bullet)

        # Check if the boost state has ended
        if player['boosted'] and current_time - player['boost_start_time'] >= boost_duration and paused == False:
            player['speed'] //= 1.5
            player['boosted'] = False
            boost_cooldown_start_time = current_time

        # Move stars
        for star in stars:
            star['pos'][1] += star['speed']
            if star['pos'][1] > height:
                star['pos'][1] = 0
                star['pos'][0] = random.randint(0, width)

        # Drawing
        screen.fill(BLACK)

        # Draw stars
        for star in stars:
            pygame.draw.circle(screen, WHITE, (int(star['pos'][0]), int(star['pos'][1])), 1)

        # Draw player
        player_center = (player['rect'].centerx, player['rect'].centery)
        if player['boosted']:
            pygame.draw.polygon(screen, ORANGE, [
                (player_center[0], player_center[1] - int(player_size * 1.5) // 2),
                (player_center[0] - int(int(player_size * 1.5) * math.sqrt(3) / 4),
                 player_center[1] + int(player_size * 1.5) // 4),
                (player_center[0] + int(int(player_size * 1.5) * math.sqrt(3) / 4),
                 player_center[1] + int(player_size * 1.5) // 4)
            ])
        else:
            pygame.draw.polygon(screen, RED, [
                (player_center[0], player_center[1] - int(player_size * 1.5) // 2),
                (player_center[0] - int(int(player_size * 1.5) * math.sqrt(3) / 4),
                 player_center[1] + int(player_size * 1.5) // 4),
                (player_center[0] + int(int(player_size * 1.5) * math.sqrt(3) / 4),
                 player_center[1] + int(player_size * 1.5) // 4)
            ])

        # Inside the main game loop, draw triangles
        for triangle in triangles:
            rotated_triangle = pygame.transform.rotate(pygame.Surface((40, 40)), 180)  # Rotate the triangle 180 degrees
            rotated_triangle_rect = rotated_triangle.get_rect(center=triangle['rect'].center)
            pygame.draw.polygon(rotated_triangle, COLOUR, [
                (0, 0),
                (40, 0),
                (20, 40)
            ])
            screen.blit(rotated_triangle, rotated_triangle_rect)


        # Draw bullets
        for bullet in player_bullets:
            pygame.draw.rect(screen, WHITE, bullet)
        for bullet in enemy_bullets:
            pygame.draw.rect(screen, COLOUR, bullet)
        for enemy in enemies:
            pygame.draw.rect(screen, COLOUR, enemy['rect'])

        draw_text(screen, 'Score: ' + str(score), WHITE, (10, 10))
        draw_text(screen, 'High Score: ' + str(high_score), WHITE, (10, 50))

        # Refresh screen
        pygame.display.flip()
        pygame.time.Clock().tick(60)



pygame.quit()