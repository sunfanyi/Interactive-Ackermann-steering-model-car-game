import pygame

pygame.init()

# Set up the Pygame display
screen_width = 640
screen_height = 480
display_surface = pygame.display.set_mode((screen_width, screen_height))

# Load two images for the screens
image1 = pygame.image.load('CWMap.jpg')
image2 = pygame.image.load('Gantt Chart Example.png')

# Create two Pygame Surface objects for the screens
screen1 = pygame.Surface((screen_width, screen_height))
screen2 = pygame.Surface((140, 180))

# Fill the screens with the images
screen1.blit(image1, (0, 0))
screen2.blit(image2, (0, 0))

# Set the initial screen to display
current_screen = screen1

# Run the Pygame event loop
while True:
    # Handle Pygame events
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
            quit()

    # Draw the current screen to the display surface
    display_surface.blit(screen1, (0, 0))
    display_surface.blit(screen2, (300, 300))

    # Update the Pygame display
    pygame.display.update()

