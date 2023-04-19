import pygame
import sys

# Initialize pygame
pygame.init()

# Create a display surface
screen = pygame.display.set_mode((800, 600))
pygame.display.set_caption('Zoom In Animation')

# Create a subwindow (surface) with some content
subwindow = pygame.Surface((400, 300))
subwindow.fill((255, 0, 0))
pygame.draw.circle(subwindow, (0, 255, 0), (200, 150), 100)

# Animation parameters
zoom_duration = 3  # seconds
frame_rate = 60
frames = int(zoom_duration * frame_rate)
current_frame = 0

clock = pygame.time.Clock()

# Main loop
running = True
while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
            break

    # Clear the screen
    screen.fill((0, 0, 0))

    # Calculate the current scale factor
    scale_factor = current_frame / frames

    # Scale the subwindow
    scaled_width = int(400 * scale_factor)
    scaled_height = int(300 * scale_factor)
    scaled_subwindow = pygame.transform.scale(subwindow, (scaled_width, scaled_height))

    # Calculate the position to center the scaled subwindow
    x = (800 - scaled_width) // 2
    y = (600 - scaled_height) // 2

    # Draw the scaled subwindow on the screen
    screen.blit(scaled_subwindow, (x, y))

    # Update the display
    pygame.display.flip()

    # Increment the current frame
    current_frame += 1
    if current_frame > frames:
        current_frame = 0

    clock.tick(frame_rate)

pygame.quit()
sys.exit()