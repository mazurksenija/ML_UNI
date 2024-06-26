import pygame
import math
from datetime import datetime

# Start pygame
pygame.init()

# Screen
screen_width = 600
screen_height = 600
screen = pygame.display.set_mode((screen_width, screen_height))
pygame.display.set_caption("Analog Clock")

# Colors
black = (0, 0, 0)
white = (255, 255, 255)
red = (255, 0, 0)
green = (0, 255, 0)
blue = (0, 0, 255)

# Sizes for clock
clock_radius = 250
clock_center = (screen_width // 2, screen_height // 2)
clock = pygame.time.Clock()

def draw_clock_face(surface):
    pygame.draw.circle(surface, white, clock_center, clock_radius)
    pygame.draw.circle(surface, black, clock_center, clock_radius, 5)
    for i in range(12):
        angle = math.radians((360 / 12) * i - 90)
        x = clock_center[0] + math.cos(angle) * (clock_radius - 20)
        y = clock_center[1] + math.sin(angle) * (clock_radius - 20)
        pygame.draw.circle(surface, black, (int(x), (int(y))), 5)

def draw_hand(surface, angle, length, color, width):
    end_x = clock_center[0] + math.cos(math.radians(angle)) * length
    end_y = clock_center[1] + math.sin(math.radians(angle)) * length
    pygame.draw.line(surface, color, clock_center, (int(end_x), int(end_y)), width)

def get_time_angles():
    now = datetime.now()
    hours = now.hour % 12
    minutes = now.minute
    seconds = now.second

    hour_angle = (360 / 12) * (hours + minutes / 60.0) - 90
    minute_angle = (360 / 60) * minutes - 90
    second_angle = (360 / 60) * seconds - 90

    return hour_angle, minute_angle, second_angle

def main():
    run = True
    while run:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                run = False

        screen.fill(black)

        draw_clock_face(screen)

        hour_angle, minute_angle, second_angle = get_time_angles()

        # print of angles of hands
        print(f"Hour angle: {hour_angle}, Minute angle: {minute_angle}, Second angle: {second_angle}")

        # clock hands
        draw_hand(screen, hour_angle, clock_radius * 0.5, green, 8)   # Hour
        draw_hand(screen, minute_angle, clock_radius * 0.75, blue, 6) # Minute
        draw_hand(screen, second_angle, clock_radius * 0.9, red, 2)   # Second

        pygame.display.flip()
        clock.tick(60)

    pygame.quit()

if __name__ == "__main__":
    main()

