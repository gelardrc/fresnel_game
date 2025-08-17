import pygame
import math
import pygame_gui
import sys

# Inicializa o pygame
pygame.init()

# Tamanho da janela
LARGURA, ALTURA = 800, 600
janela = pygame.display.set_mode((LARGURA, ALTURA))
pygame.display.set_caption("Antenas RX/TX")

# Gerenciador da GUI
manager = pygame_gui.UIManager((LARGURA, ALTURA))

box_width = 50

# Labels
rx_label = pygame_gui.elements.UILabel(
    relative_rect=pygame.Rect((LARGURA-220, box_width*0), (100, box_width)),
    text='RX Height:',
    manager=manager
)
tx_label = pygame_gui.elements.UILabel(
    relative_rect=pygame.Rect((LARGURA-220, box_width*1), (100, box_width)),
    text='TX Height:',
    manager=manager
)
dist_label = pygame_gui.elements.UILabel(
    relative_rect=pygame.Rect((LARGURA-220, box_width*2), (100, box_width)),
    text='Distance:',
    manager=manager
)

# Caixas de texto
rx_high_text = pygame_gui.elements.UITextEntryLine(
    relative_rect=pygame.Rect((LARGURA-120, box_width*0), (100, box_width)),
    manager=manager
)

tx_high_text = pygame_gui.elements.UITextEntryLine(
    relative_rect=pygame.Rect((LARGURA-120, box_width*1), (100, box_width)),
    manager=manager
)

distance_text = pygame_gui.elements.UITextEntryLine(
    relative_rect=pygame.Rect((LARGURA-120, box_width*2), (100, box_width)),
    manager=manager
)

# Botão
botao = pygame_gui.elements.UIButton(
    relative_rect=pygame.Rect((LARGURA-120, box_width*3), (100, box_width)),
    text='Atualizar',
    manager=manager
)

# Posição e altura da antena
rx_pose = [200, 500]
rx_high = 100
tx_high = 100
distance = 100

# Função para desenhar antena
def draw_antena(pose, high, cor):
    pygame.draw.rect(janela, cor, (pose[0], pose[1]-high, 10, high))

# Função para atualizar valores
def atualizar_valores():
    global rx_high, tx_high, distance
    try:
        rx_high = int(rx_high_text.get_text())
        tx_high = int(tx_high_text.get_text())
        distance = int(distance_text.get_text())
    except ValueError:
        pass

def draw_earth():
    pygame.draw.arc(janela,(0,0,255))

def draw_filled_semicircle(surface, color, center, radius, direction='up'):
    """Desenha um semi-círculo preenchido.
    direction: 'up', 'down', 'left', 'right'"""
    points = [center]
    steps = 50  # define a "suavidade" do semi-círculo
    if direction == 'up':
        for i in range(steps + 1):
            angle = math.pi * i / steps
            x = center[0] + radius * math.cos(angle)
            y = center[1] - radius * math.sin(angle)
            points.append((x, y))
    elif direction == 'down':
        for i in range(steps + 1):
            angle = math.pi * i / steps
            x = center[0] + radius * math.cos(angle)
            y = center[1] + radius * math.sin(angle)
            points.append((x, y))
    elif direction == 'left':
        for i in range(steps + 1):
            angle = math.pi * i / steps
            x = center[0] - radius * math.sin(angle)
            y = center[1] + radius * math.cos(angle)
            points.append((x, y))
    elif direction == 'right':
        for i in range(steps + 1):
            angle = math.pi * i / steps
            x = center[0] + radius * math.sin(angle)
            y = center[1] + radius * math.cos(angle)
            points.append((x, y))

    pygame.draw.polygon(surface, color, points)


# Loop principal
clock = pygame.time.Clock()
while True:
    time_delta = clock.tick(60)/1000.0

    for evento in pygame.event.get():
        if evento.type == pygame.QUIT:
            pygame.quit()
            sys.exit()

        # Movimentação com setas
        elif evento.type == pygame.KEYDOWN:
            if evento.key == pygame.K_UP:
                rx_high += 5
            elif evento.key == pygame.K_DOWN:
                rx_high -= 5
            elif evento.key == pygame.K_RIGHT:
                rx_pose[0] += 5
            elif evento.key == pygame.K_LEFT:
                rx_pose[0] -= 5

        # Passa eventos para a GUI
        manager.process_events(evento)

        # Clique no botão
        if evento.type == pygame_gui.UI_BUTTON_PRESSED:
            if evento.ui_element == botao:
                atualizar_valores()

        # Quando termina de digitar na caixa
        if evento.type == pygame_gui.UI_TEXT_ENTRY_FINISHED:
            if evento.ui_element in [rx_high_text, tx_high_text, distance_text]:
                atualizar_valores()

    # Atualiza a GUI
    manager.update(time_delta)

    # Preenche o fundo
    janela.fill((0, 0, 0))

    # Desenha antenas
    draw_antena(rx_pose, rx_high, (255, 255, 255))
    tx_x = min(rx_pose[0] + distance, LARGURA - 10)
    draw_antena([tx_x, rx_pose[1]], tx_high, (0, 255, 0))

    # Exibe valores na tela
    font = pygame.font.SysFont(None, 24)
    info_text = font.render(f"RX: {rx_high} | TX: {tx_high} | Dist: {distance}", True, (255, 255, 0))
    janela.blit(info_text, (10, 10))

    draw_filled_semicircle(janela, (255, 0, 0), (200, 200), 100, direction='up')


    # Desenha a GUI
    manager.draw_ui(janela)

    pygame.display.flip()
