from pygame import *
import socket
import json
from threading import Thread

WIDTH, HEIGHT = 800, 600

init()
screen = display.set_mode((WIDTH, HEIGHT))
clock = time.Clock()
display.set_caption("Пінг-Понг")

background = image.load("пинг фон.png")
background = transform.scale(background, (WIDTH, HEIGHT))

overlay = Surface((WIDTH, HEIGHT))
overlay.set_alpha(120)
overlay.fill((0, 0, 0))

font_big = font.Font(None, 72)
font_main = font.Font(None, 36)

def connect_to_server():
    while True:
        try:
            client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            client.connect(('localhost', 8080))
            my_id = int(client.recv(24).decode())
            return my_id, client
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

my_id, client = connect_to_server()
game_state = {}

Thread(target=receive, daemon=True).start()

while True:
    for e in event.get():
        if e.type == QUIT:
            exit()

    screen.blit(background, (0, 0))
    screen.blit(overlay, (0, 0))

    if "event_countdown" in game_state and game_state["event_countdown"] > 0:
        t = font_big.render(str(game_state["event_countdown"]), True, (255, 255, 0))
        screen.blit(t, t.get_rect(center=(WIDTH//2, HEIGHT//2)))

    elif "event_timer" in game_state:
        timer = font_main.render(f"Подія через: {game_state['event_timer']}", True, (255,255,255))
        screen.blit(timer, (WIDTH//2 - 80, 50))

    if "current_event" in game_state and game_state["current_event"]:
        if game_state["current_event"] == 1:
            txt = "⚡ М'яч прискорено!"
        else:
            txt = "🟢 Платформи швидше!"
        t = font_main.render(txt, True, (0,255,0))
        screen.blit(t, (WIDTH//2 - 120, 80))

    if "paddles" in game_state:
        draw.rect(screen, (0,255,0),(20, game_state['paddles']['0'],20,100))
        draw.rect(screen, (255,0,255),(WIDTH-40, game_state['paddles']['1'],20,100))
        draw.circle(screen, (255,255,255),(int(game_state['ball']['x']), int(game_state['ball']['y'])),10)

    display.update()
    clock.tick(60)

    keys = key.get_pressed()
    if keys[K_w]:
        client.send(b"UP")
    elif keys[K_s]:
        client.send(b"DOWN")

