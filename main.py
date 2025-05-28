import pygame
import math
import random  # Replace with your UART reading logic
import time

def draw_cross(surface, center, size=10, color=(255, 255, 255)):
    x, y = center
    pygame.draw.line(surface, color, (x - size//2, y), (x + size//2, y), 2)
    pygame.draw.line(surface, color, (x, y - size//2), (x, y + size//2), 2)

def get_uart_parameters():
    # TODO: Replace this with actual UART reading logic
    # Example: return distance, tilt_deg
    distance = 400 #random.randint(400, 800)
    tilt_deg = 45 #random.uniform(-10, 10)
    return distance, tilt_deg

def main(width=1000, height=600):
    pygame.init()
    screen = pygame.display.set_mode((width, height))
    clock = pygame.time.Clock()

    running = True
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

        # Get parameters from UART (mocked here)
        distance, tilt_deg = get_uart_parameters()

        # Draw
        screen.fill((0, 0, 0))
        cx, cy = width // 2, height // 2
        half_dist = distance / 2
        tilt_rad = math.radians(tilt_deg)
        dx = math.cos(tilt_rad) * half_dist
        dy = math.sin(tilt_rad) * half_dist
        pt1 = (int(cx - dx), int(cy - dy))
        pt2 = (int(cx + dx), int(cy + dy))
        draw_cross(screen, pt1)
        draw_cross(screen, pt2)
        pygame.display.flip()

        clock.tick(60)  # 60 FPS

    pygame.quit()

if __name__ == "__main__":
    main()