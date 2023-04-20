import pygame
import sys
import numpy as np

import game_function as gf
from trajectory_planning import get_path, do_trajectory_planning

# Initialize pygame
pygame.init()

# Create a display surface
screen = pygame.display.set_mode((800, 600))
pygame.display.set_caption('Manipulator')

frame_rate = 60

clock = pygame.time.Clock()

pointer = 0
end_memory = []

res = 20  # resolution of trajectory points
paths = do_trajectory_planning(res)
P_coordinates = paths[4]
num_points = len(paths[0])

while True:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
            sys.exit()

    screen.fill((255, 255, 255))
    joints = get_path(paths, pointer, end_memory)

    for end_pos in end_memory:
        pos2d = gf.point_3d_to_2d(*end_pos, offset=(400, 300))
        pygame.draw.circle(screen, (255, 0, 0), pos2d, 3)

    # plot via points
    last_via_points = P_coordinates[pointer//res:pointer//res+2, :]
    for point in last_via_points:
        pos2d = gf.point_3d_to_2d(*point, offset=(400, 300))
        pygame.draw.circle(screen, (0, 255, 0), pos2d, 3)

    joints = [gf.point_3d_to_2d(*joint, offset=(400, 300))
              for joint in joints]

    for i in range(len(joints) - 1):
        P1 = joints[i]
        P2 = joints[i + 1]
        # plot links
        pygame.draw.line(screen, (0, 0, 255), P1, P2, 2)
        # plot joints
        pygame.draw.circle(screen, (0, 0, 0), P1, 3)

    pointer += 1
    if pointer >= num_points:
        pointer = 0

    pygame.display.flip()
    clock.tick(frame_rate)


