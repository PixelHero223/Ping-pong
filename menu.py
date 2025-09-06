import pygame
import subprocess
import sys

pygame.init()

WIDTH, HEIGHT = 600, 400
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
BLUE = (0, 191, 255)
RED = (255, 69, 0)

screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Меню Пінг-Понг")

font = pygame.font.SysFont("Arial", 40)
clock = pygame.time.Clock()


def draw_button(text, x, y, w, h, color):
    pygame.draw.rect(screen, color, (x, y, w, h))
    txt = font.render(text, True, WHITE)
    screen.blit(txt, (x + w // 2 - txt.get_width() // 2, y + h // 2 - txt.get_height() // 2))


def main_menu():
    running = True
    while running:
        screen.fill(BLACK)

        draw_button("почати мач", 200, 120, 200, 60, BLUE)
        draw_button("вийти", 200, 220, 200, 60, RED)

        mx, my = pygame.mouse.get_pos()
        click = pygame.mouse.get_pressed()

        if 200 < mx < 400 and 120 < my < 180:
            if click[0]:
                subprocess.Popen([sys.executable, "client.py"])
                running = False

        if 200 < mx < 400 and 220 < my < 280:
            if click[0]:
                running = False

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

        pygame.display.update()
        clock.tick(60)


if __name__ == "__main__":
    main_menu()
    pygame.quit()
