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

def draw_cross(surface, center, size=15, color=(255, 255, 255)):
    x, y = center
    pygame.draw.line(surface, color, (x - size//2, y), (x + size//2, y), 2)
    pygame.draw.line(surface, color, (x, y - size//2), (x, y + size//2), 2)

def compute_point_positions_mm(distance_mm, beam_angle_deg, separation_mm):
    """
    Given the distance to the wall (in mm), the beam angle (in degrees),
    and the desired separation between two projected points (in mm),
    return the normalized horizontal positions (-x, +x) within the beam.
    
    Returns:
        (x_left, x_right): positions as a tuple of normalized values (-1.0 to +1.0)
    """
    # Convert to meters
    distance_m = distance_mm / 1000.0
    separation_m = separation_mm / 1000.0

    # Calculate half beam angle in radians
    half_angle_rad = math.radians(beam_angle_deg / 2)

    # Compute total beam width at the wall
    beam_width_m = 2 * distance_m * math.tan(half_angle_rad)

    # Compute normalized offset
    x = separation_m / beam_width_m / 2

    # Return symmetric positions relative to beam center
    return ( x * 2 )

def serial_reader(ser):
    global serial_data
    while True:
        try:
            line = ser.readline().decode('utf-8').strip()
            if line:
                parts = line.split(',')
                if len(parts) >= 2:
                    distance = float(parts[0])
                    tilt_deg = float(parts[1])
                    print(distance, tilt_deg)
                    with data_lock:
                        serial_data["distance"] = distance
                        serial_data["tilt_deg"] = tilt_deg
        except Exception:
            pass

def main(width=1980, height=1080, serial_port='/dev/ttyACM0', baudrate=115200):
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
            if (serial_data["distance"] != 0):
                distance = compute_point_positions_mm(serial_data["distance"], 46, 800000)
                #print(distance)
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