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
tx_angle = math.pi/2
rx_high = 100
tx_high = 100
distance = 100
earth_radius = 500  
earth_center = (LARGURA/2, ALTURA+earth_radius/2)

# Variável para rotação
earth_angle = 0
velocidade_rotacao = 10  # graus por segundo


#earth_center = (LARGURA/2, earth_radius/2)
ceu = pygame.image.load("ceu.jpg").convert_alpha()
ceu = pygame.transform.scale(ceu, (LARGURA, ALTURA))

earth_pic = pygame.image.load("earth.png").convert_alpha()
earth_pic = pygame.transform.scale(earth_pic, (2*earth_radius, earth_radius))  # largura = 2r, altura = r


sprite_antena = pygame.image.load("antena.png").convert_alpha()
 
ceu_offset = 0  
velocidade_ceu = 50  # pixels por segundo

#sprite_antena = pygame.transform.scale(sprite_antena, (40, 80))  # ajuste de tamanho

# Função para desenhar antena com sprite
def draw_antena(pose, high, cor):
    # Base da antena está em pose[0], pose[1]
    # Redimensiona de acordo com "high"
    antena_resized = pygame.transform.scale(sprite_antena, (40, high))

    # A base da antena é alinhada embaixo
    rect = antena_resized.get_rect(midbottom=(pose[0], pose[1]))
    janela.blit(antena_resized, rect)

# Função para atualizar valores
def atualizar_valores():
    global rx_high, tx_high, distance
    try:
        rx_high = int(rx_high_text.get_text())
        tx_high = int(tx_high_text.get_text())
        distance = int(distance_text.get_text())
    except ValueError:
        pass

#def draw_earth():
#    pygame.draw.arc(janela,(0,0,255))

def draw_earth(surface, color, center, radius, direction='up'):
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
    
def draw_los(rx_pose,tx_pose,rx_high,tx_high):
    # Topo da TX
    tx_top = (tx_pose[0], tx_pose[1] - tx_high)

    # Topo da RX
    rx_top = (rx_pose[0], rx_pose[1] - rx_high)

    # Linha de visada (amarela)
    pygame.draw.line(janela, (255, 255, 0), tx_top, rx_top, 2)
def draw_earth_sprite(surface, center, radius):
    # Redimensiona sempre que mudar o raio
    
    earth_resized = pygame.transform.scale(earth_pic, (2.6*radius, 2.1*radius))
    
    # Coloca a Terra centralizada no mesmo ponto que o semi-círculo
    rect = earth_resized.get_rect(center=(center[0], center[1]))
    surface.blit(earth_resized, rect)

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
                earth_radius+=5
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

    ceu_offset -= velocidade_ceu * time_delta
    if ceu_offset <= -LARGURA:  # reset quando sair da tela
        ceu_offset = 0

    # Desenha o fundo duas vezes para criar o loop
    janela.blit(ceu, (ceu_offset, 0))
    janela.blit(ceu, (ceu_offset + LARGURA, 0))

    # Atualiza a GUI
    manager.update(time_delta)

    
    draw_earth(janela, (0,0,255), earth_center, earth_radius, direction='up')
    draw_earth_sprite(janela, earth_center, earth_radius)

    # Desenha antenas

    tx_pose = [ earth_center[0]+earth_radius*math.cos(-tx_angle),
                earth_center[1]+earth_radius*math.sin(-tx_angle)]
    
    draw_antena(tx_pose, tx_high, (0, 255, 0))
    
    theta = distance/earth_radius ## comprimento do arco distance = r*theta

    rx_theta = tx_angle - theta

    rx_pose = [ earth_center[0]+earth_radius*math.cos(-rx_theta),
                earth_center[1]+earth_radius*math.sin(-rx_theta)]
    
    draw_antena(rx_pose, rx_high, (255, 0, 0))
    
    draw_los(rx_pose,tx_pose,rx_high,tx_high)
    
    

    # Exibe valores na tela
    font = pygame.font.SysFont(None, 24)
    info_text = font.render(f"RX: {rx_high} | TX: {tx_high} | Dist: {distance}", True, (255, 255, 0))
    janela.blit(info_text, (10, 10))



    # Desenha a GUI
    manager.draw_ui(janela)

    pygame.display.flip()