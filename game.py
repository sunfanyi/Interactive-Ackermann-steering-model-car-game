import pygame
import math
import numpy as np
from car import Car


def rotation(theta, direction):
    if direction == 'x':
        R = np.array([[1, 0, 0],
                      [0, np.cos(theta), -np.sin(theta)],
                      [0, np.sin(theta), np.cos(theta)]])
    elif direction == 'y':
        R = np.array([[np.cos(theta), 0, np.sin(theta)],
                      [0, 1, 0],
                      [-np.sin(theta), 0, np.cos(theta)]])
    elif direction == 'z':
        R = np.array([[np.cos(theta), -np.sin(theta), 0],
                      [np.sin(theta), np.cos(theta), 0],
                      [0, 0, 1]])
    return R


def add_translation(R, t=np.array([0, 0, 0, 1])):
    T = np.vstack([R, np.array([[0, 0, 0]])])
    T = np.hstack([T, t.reshape(-1, 1)])
    return T


def point_3d_to_2d(x, y, z):
    # for x: 800 = screen length, 5000 = image length, 2 = scale factor (reduce to make larger)
    x_factor = 800/5000/2
    y_factor = 600/3600/1.5
    z_factor = 0.1

    x *= x_factor
    y *= y_factor
    z *= z_factor

    x_rotation = rotation(120/180 * np.pi, 'x').T
    z_rotation = rotation(-15/180 * np.pi, 'z').T

    R = np.matmul(x_rotation, z_rotation)

    x_2d, y_2d, z_2d = np.matmul(R, np.array([x, y, z]))

    return x_2d, y_2d


def draw_axes(screen, origin_2d):
    origin_x, origin_y = origin_2d

    origin_3d = [0, 0, 0]
    xpoint = [5224, 0, 0]
    ypoint = [0, 3680, 0]
    zpoint = [0, 0, 500]

    x_tick_interval = 500
    y_tick_interval = 500
    z_tick_interval = 500
    tick_interval = 500

    font_axes = pygame.font.Font(None, 24)  # font for axes labels
    font_tick = pygame.font.Font(None, 18)  # font for tick labels
    axes_color = (0, 0, 0)
    tick_color = (100, 100, 100)

    # Draw X-axis
    line = [origin_3d, xpoint]
    _, xpoint_2d = draw_line(screen, line, origin_2d, axes_color, 2)
    x_label = font_axes.render("X", True, axes_color)
    screen.blit(x_label, xpoint_2d)
    for i in range(0, xpoint[0] + tick_interval, tick_interval):
        tick_x, tick_y = point_3d_to_2d(i, 0, 0)
        tick_label = font_tick.render(str(i), True, tick_color)
        screen.blit(tick_label, (origin_x + tick_x - 10, origin_y - tick_y))

    # Draw Y-axis
    line = [origin_3d, ypoint]
    _, ypoint_2d = draw_line(screen, line, origin_2d, axes_color, 2)
    y_label = font_axes.render("Y", True, axes_color)
    screen.blit(y_label, ypoint_2d)
    for i in range(0, ypoint[1] + tick_interval, tick_interval):
        tick_x, tick_y = point_3d_to_2d(0, i, 0)
        tick_label = font_tick.render(str(i), True, tick_color)
        screen.blit(tick_label, (origin_x + tick_x - 10, origin_y - tick_y))

    # Draw Z-axis
    line = [origin_3d, zpoint]
    _, zpoint_2d = draw_line(screen, line, origin_2d, axes_color, 2)
    z_label = font_axes.render("Z", True, axes_color)
    screen.blit(z_label, zpoint_2d)
    for i in range(0, zpoint[2] + tick_interval, tick_interval):
        tick_x, tick_y = point_3d_to_2d(0, 0, i)
        tick_label = font_tick.render(str(i), True, tick_color)
        screen.blit(tick_label, (origin_x + tick_x - 10, origin_y - tick_y))


def main():
    scalr = 40
    mycar = Car(length=5*scalr, width=2*scalr, height=1.5*scalr,
                wheel_radius=0.5*scalr, wheel_width=0.3*scalr,
                wheel_offset=0.2*scalr, wheel_base=3*scalr)

    R = (255, 0, 0)
    G = (0, 255, 0)
    B = (0, 0, 255)
    K = (0, 0, 0)
    pygame.init()
    display = (800, 600)
    screen = pygame.display.set_mode(display)
    pygame.display.set_caption('3D Axes in Pygame')

    origin = (250, 200)
    x, y, z = 0, 0, 0
    delta_x, delta_y, delta_z = 0.1, 0.15, 0.2

    running = True
    i = 0
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

        x += delta_x
        y += delta_y
        z += delta_z

        if x > 5 or x < -5:
            delta_x = -delta_x
        if y > 5 or y < -5:
            delta_y = -delta_y
        if z > 5 or z < -5:
            delta_z = -delta_z

        screen.fill((255, 255, 255))
        draw_axes(screen, origin)

        origin_x, origin_y = origin
        x_end, y_end = point_3d_to_2d(2000, 0, 0)
        pygame.draw.circle(screen, R, (origin_x + x_end, origin_y - y_end), 5)
        x_end, y_end = point_3d_to_2d(0, 2000, 0)
        pygame.draw.circle(screen, G, (origin_x + x_end, origin_y - y_end), 5)
        x_end, y_end = point_3d_to_2d(0, 0, 2000)
        pygame.draw.circle(screen, B, (origin_x + x_end, origin_y - y_end), 5)

        example_point = [500, 500, 500]
        x_end, y_end = point_3d_to_2d(500, 500, 500)
        point = (origin_x + x_end, origin_y - y_end)
        pygame.draw.circle(screen, K, point, 5)

        lines = (example_point, [0, 500, 500])
        draw_line(screen, lines, origin, K)

        lines = (example_point, [500, 0, 500])
        draw_line(screen, lines, origin, K)

        lines = (example_point, [500, 500, 0])
        draw_line(screen, lines, origin, K)

        R_mat = rotation(-np.pi - i / 10, 'z')
        T_mat = add_translation(R_mat, np.array([i * 10, 3000, 0, 1]))
        bodylines = mycar.plot_body(T_mat)
        for line in bodylines:
            draw_line(screen, line, origin)

        pygame.display.flip()
        pygame.time.wait(20)
        i+=1

    pygame.quit()


def draw_line(screen, line, oringin, color=(0, 0, 0), linewidth=1):
    p1 = line[0]
    p2 = line[1]

    x1_2d, y1_2d = point_3d_to_2d(p1[0], p1[1], p1[2])
    x2_2d, y2_2d = point_3d_to_2d(p2[0], p2[1], p2[2])

    p1_2d = (oringin[0] + x1_2d, oringin[1] - y1_2d)
    p2_2d = (oringin[0] + x2_2d, oringin[1] - y2_2d)

    pygame.draw.line(screen, color, p1_2d, p2_2d, linewidth)

    return p1_2d, p2_2d

if __name__ == "__main__":
    main()
