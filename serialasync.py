import pygame
import math
import serial
import threading

# Shared state for serial data
serial_data = {
    "distance": 400,
    "tilt_deg": 0
}
data_lock = threading.Lock()

def draw_cross(surface, center, size=10, color=(255, 255, 255)):
    x, y = center
    pygame.draw.line(surface, color, (x - size//2, y), (x + size//2, y), 2)
    pygame.draw.line(surface, color, (x, y - size//2), (x, y + size//2), 2)

def serial_reader(ser):
    global serial_data
    while True:
        try:
            line = ser.readline().decode('utf-8').strip()
            if line:
                parts = line.split(',')
                if len(parts) == 2:
                    distance = float(parts[0])
                    tilt_deg = float(parts[1])
                    with data_lock:
                        serial_data["distance"] = distance
                        serial_data["tilt_deg"] = tilt_deg
        except Exception:
            pass

def main(width=1000, height=600, serial_port='/dev/ttyUSB0', baudrate=9600):
    pygame.init()
    screen = pygame.display.set_mode((width, height))
    clock = pygame.time.Clock()

    # Open serial port
    ser = serial.Serial(serial_port, baudrate, timeout=0.2)


    # Start serial reader thread
    t = threading.Thread(target=serial_reader, args=(ser,), daemon=True)
    t.start()

    running = True
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

        # Get latest parameters (thread-safe)
        with data_lock:
            distance = serial_data["distance"]
            tilt_deg = serial_data["tilt_deg"]

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

    ser.close()
    pygame.quit()

if __name__ == "__main__":
    main()