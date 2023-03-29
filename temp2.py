import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import pygame
import io

class LatexWindow:
    def __init__(self, settings, screen):
        self.settings = settings
        self.screen = screen

        fig = plt.figure(figsize=(6, 4), dpi=10)
        fig.patch.set_visible(False)
        self.ax = fig.add_axes([0, 0, 1, 1])
        self.ax.axis('off')

        self.cache = {}
        self.fig_surface = None
        self.update('Hello, world!')

    def update(self, text):
        if text in self.cache:
            self.fig_surface = self.cache[text]
        else:
            self.ax.clear()
            self.ax.axis('off')
            self.ax.text(0.5, 0.5, text, ha='center', va='center', fontsize=36)

            buf = io.BytesIO()
            plt.savefig(buf, format='png', dpi=10, bbox_inches='tight', pad_inches=0)
            buf.seek(0)

            fig_surface = pygame.image.load(buf)
            self.cache[text] = fig_surface
            self.fig_surface = fig_surface

    def draw(self):
        self.screen.blit(self.fig_surface, (0, 0))