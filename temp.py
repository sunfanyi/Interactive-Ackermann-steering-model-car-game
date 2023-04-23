import pygame
import sys

pygame.init()

# Set up the display
screen = pygame.display.set_mode((800, 600))

# Create a font object
font = pygame.font.Font(None, 36)

# Start the timer
start_time = pygame.time.get_ticks()

# Main game loop
running = True
while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
            break

    # Update game state and draw here

    # Clear the screen
    screen.fill((255, 255, 255))

    # Calculate the elapsed time
    elapsed_time = (pygame.time.get_ticks() - start_time) / 1000

    # Render the elapsed time as text with two decimal places
    timer_text = font.render(f"Elapsed time: {elapsed_time:.2f} seconds", True, (0, 0, 0))

    # Display the timer text on the screen
    screen.blit(timer_text, (10, 10))

    # Update the display
    pygame.display.flip()

pygame.quit()
sys.exit()