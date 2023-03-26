import cv2
import numpy as np
import pygame

# Load image
img = cv2.imread('CWMap.jpg')

# Convert image to RGB and flip horizontally
rgb_img = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
# rgb_img = np.fliplr(rgb_img)

# Create Pygame surface with same size as image
surface = pygame.surfarray.make_surface(rgb_img)

# Scale image down to fit screen
scale_factor = min(800 / surface.get_width(), 600 / surface.get_height())
scaled_surface = pygame.transform.scale(surface, (int(surface.get_width() * scale_factor),
                                                   int(surface.get_height() * scale_factor)))

# Display scaled surface
pygame.init()
screen = pygame.display.set_mode((800, 600))
screen.blit(scaled_surface, (0, 0))
pygame.display.update()
while True:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
            quit()