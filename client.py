from pygame import *
import socket
import json
from threading import Thread

# -------------------- НАЛАШТУВАННЯ --------------------
WIDTH, HEIGHT = 800, 600
PADDLE_W, PADDLE_H = 20, 100

# -------------------- PYGAME INIT --------------------
init()
screen = display.set_mode((WIDTH, HEIGHT))
display.set_caption("фон.png")
clock = time.Clock()

# -------------------- СПРАЙТИ ПЛАТФОРМ --------------------
# sprite sheet: 40x100 (2 кадри по 20x100)

blue_sheet = image.load("platform1.png").convert_alpha()
red_sheet = image.load("platform2.png").convert_alpha()

# вирізання кадрів
blue_visible = blue_sheet.subsurface((0, 0, PADDLE_W, PADDLE_H))
blue_black   = blue_sheet.subsurface((PADDLE_W, 0, PADDLE_W, PADDLE_H))

red_visible  = red_sheet.subsurface((0, 0, PADDLE_W, PADDLE_H))
red_black    = red_sheet.subsurface((PADDLE_W, 0, PADDLE_W, PADDLE_H))

# -------------------- МЕРЕЖА --------------------
def connect_to_server():
    while True:
        try:
            client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            client.connect(("localhost", 8080))
            pid = int(client.recv(32).decode())
            return pid, client
        except:
            pass

def receive():
    global game_state
    buffer = ""
    while True:
        try:
            data = client.recv(1024).decode()
            buffer += data
            while "\n" in buffer:
                packet, buffer = buffer.split("\n", 1)
                if packet.strip():
                    game_state = json.loads(packet)
        except:
            break

player_id, client = connect_to_server()
game_state = {}

Thread(target=receive, daemon=True).start()

# -------------------- ГОЛОВНИЙ ЦИКЛ --------------------
running = True
while running:
    for e in event.get():
        if e.type == QUIT:
            running = False

    screen.fill((0, 0, 0))

    if "paddles" in game_state and "ball" in game_state:

        # вибір кадру
        if game_state.get("invisible_paddles"):
            left_img = blue_black
            right_img = red_black
        else:
            left_img = blue_visible
            right_img = red_visible

        # платформи
        screen.blit(left_img, (20, game_state["paddles"]["0"]))
        screen.blit(right_img, (WIDTH - 40, game_state["paddles"]["1"]))

        # м'яч
        draw.circle(
            screen,
            (255, 255, 255),
            (int(game_state["ball"]["x"]), int(game_state["ball"]["y"])),
            10
        )

    display.update()
    clock.tick(60)

    # керування (один клієнт = ліва платформа)
    keys = key.get_pressed()
    if keys[K_w]:
        client.send(b"UP")
    elif keys[K_s]:
        client.send(b"DOWN")

quit()




