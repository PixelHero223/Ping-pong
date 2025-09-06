from pygame import *
import socket
import json
from threading import Thread

# --- РОЗМІРИ ---
WIDTH, HEIGHT = 800, 600

# --- ІНІЦІАЛІЗАЦІЯ ---
init()
mixer.init()
screen = display.set_mode((WIDTH, HEIGHT))
clock = time.Clock()
display.set_caption("Пінг-Понг")

# --- КОЛЬОРИ ---
GREEN = (34, 139, 34)
WHITE = (255, 255, 255)
PLAYER1_COLOR = (0, 191, 255)
PLAYER2_COLOR = (255, 69, 0)

# --- ШРИФТИ ---
font_win = font.Font(None, 72)
font_main = font.Font(None, 36)

# --- ЗВУКИ ---
wall_sound = mixer.Sound("wall.wav")
paddle_sound = mixer.Sound("paddle.wav")
win_sound = mixer.Sound("win31.wav")
lose_sound = mixer.Sound("lose.wav")

# --- СЕРВЕР ---
def connect_to_server():
    while True:
        try:
            client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            client.connect(('localhost', 8080))  # Підключення до сервера
            buffer = ""
            game_state = {}
            my_id = int(client.recv(24).decode())
            return my_id, game_state, buffer, client
        except:
            pass


def receive():
    global buffer, game_state, game_over
    while not game_over:
        try:
            data = client.recv(1024).decode()
            buffer += data
            while "\n" in buffer:
                packet, buffer = buffer.split("\n", 1)
                if packet.strip():
                    game_state = json.loads(packet)
        except:
            game_state["winner"] = -1
            break


# --- ГРА ---
game_over = False
winner = None
you_winner = None
state = "menu"  # <-- тут ми запускаємо програму з меню

my_id, game_state, buffer, client = connect_to_server()
Thread(target=receive, daemon=True).start()

while True:
    for e in event.get():
        if e.type == QUIT:
            exit()

        if state == "menu":
            if e.type == KEYDOWN:
                if e.key == K_RETURN:  # Enter – почати гру
                    state = "game"
                elif e.key == K_ESCAPE:  # Escape – вийти
                    exit()

    # --- СЦЕНА МЕНЮ ---
    if state == "menu":
        screen.fill((0, 0, 0))
        title_text = font_win.render("Пінг-Понг", True, WHITE)
        play_text = font_main.render("ENTER - Грати", True, WHITE)
        quit_text = font_main.render("ESC - Вихід", True, WHITE)

        screen.blit(title_text, (WIDTH // 2 - 150, HEIGHT // 2 - 100))
        screen.blit(play_text, (WIDTH // 2 - 100, HEIGHT // 2))
        screen.blit(quit_text, (WIDTH // 2 - 100, HEIGHT // 2 + 50))

        display.update()
        continue

    # --- СЦЕНА ГРИ ---
    if state == "game":

        # Відлік часу
        if "countdown" in game_state and game_state["countdown"] > 0:
            screen.fill((0, 0, 0))
            countdown_text = font.Font(None, 72).render(str(game_state["countdown"]), True, WHITE)
            screen.blit(countdown_text, (WIDTH // 2 - 20, HEIGHT // 2 - 30))
            display.update()
            continue

        # Кінець гри
        if "winner" in game_state and game_state["winner"] is not None:
            screen.fill((20, 20, 20))

            if you_winner is None:
                if game_state["winner"] == my_id:
                    you_winner = True
                else:
                    you_winner = False

            if you_winner:
                text = "Ти переміг!"
            else:
                text = "Пощастить наступним разом!"

            win_text = font_win.render(text, True, (255, 215, 0))
            text_rect = win_text.get_rect(center=(WIDTH // 2, HEIGHT // 2))
            screen.blit(win_text, text_rect)

            text = font_win.render('К - рестарт | M - меню', True, (255, 215, 0))
            text_rect = text.get_rect(center=(WIDTH // 2, HEIGHT // 2 + 120))
            screen.blit(text, text_rect)

            display.update()

            keys = key.get_pressed()
            if keys[K_k]:
                client.send(b"RESTART")
                you_winner = None
            if keys[K_m]:  # вихід у меню
                state = "menu"
                you_winner = None
                game_state = {}
            continue

        # Малювання гри
        if game_state:
            screen.fill(GREEN)
            draw.line(screen, WHITE, (WIDTH // 2, 0), (WIDTH // 2, HEIGHT), 5)  # центральна лінія
            draw.rect(screen, WHITE, (10, 10, WIDTH - 20, HEIGHT - 20), 5)  # розмітка по краях

            # Ракетки
            draw.rect(screen, PLAYER1_COLOR, (20, game_state['paddles']['0'], 20, 100))
            draw.rect(screen, PLAYER2_COLOR, (WIDTH - 40, game_state['paddles']['1'], 20, 100))

            # М'яч
            draw.circle(screen, WHITE, (game_state['ball']['x'], game_state['ball']['y']), 10)

            # Рахунок
            score_text = font_main.render(f"{game_state['scores'][0]} : {game_state['scores'][1]}", True, WHITE)
            screen.blit(score_text, (WIDTH // 2 - 25, 20))

            # Звуки
            if game_state['sound_event']:
                if game_state['sound_event'] == 'wall_hit':
                    wall_sound.play()
                if game_state['sound_event'] == 'platform_hit':
                    paddle_sound.play()

        else:
            wating_text = font_main.render(f"Очікування гравців...", True, WHITE)
            screen.blit(wating_text, (WIDTH // 2 - 100, HEIGHT // 2))

        display.update()
        clock.tick(60)

        # Керування
        keys = key.get_pressed()
        if keys[K_w]:
            client.send(b"UP")
        elif keys[K_s]:
            client.send(b"DOWN")