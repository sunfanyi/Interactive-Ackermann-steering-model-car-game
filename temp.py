import pygame
import pygame.freetype

pygame.init()

# Set up the display
width, height = 1000, 480
screen = pygame.display.set_mode((width, height))
pygame.display.set_caption("LaTeX-like rendering in Pygame")

# Load a font
pygame.freetype.init()
font = pygame.freetype.SysFont(None, 36)

# Define the text with LaTeX-like syntax
text = r"Hello, world! $\frac{a}{b} \times \sqrt{c}$"

# Main loop
running = True
while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

    screen.fill((0, 0, 0))

    # Render the text with LaTeX-like syntax
    font.render_to(screen, (width // 2 - 100, height // 2 - 18), text, (255, 255, 255))

    pygame.display.flip()

pygame.quit()