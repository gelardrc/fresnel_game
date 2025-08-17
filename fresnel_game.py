# fresnel_game.py
import pygame
import math

# ---------- Config inicial ----------
WIDTH, HEIGHT = 1100, 750
LEFT_PAD, RIGHT_PAD, BOTTOM_PAD, TOP_PAD = 120, 120, 180, 80  # BOTTOM_PAD ↑ para caber os sliders
FPS = 60

# Estado inicial (unidades "físicas")
D_m = 50_000.0          # distância entre antenas (m)
f_Hz = 2_000_000_000.0  # frequência (Hz)
h_tx = 40.0             # altura TX (m)
h_rx = 35.0             # altura RX (m)
obs_x = D_m * 0.4       # posição obstáculo (m) a partir do TX
obs_h = 20.0            # altura obstáculo (m)
show_curv = True
show_fresnel = True
m_per_px = 10.0         # escala vertical: quantos metros cabem em 1 pixel (↓ valor => ↑ exagero)

# Terra
R_earth = 6_371_000.0   # m
K = 4/3                 # fator K
R_eff = K * R_earth

# Pygame setup
pygame.init()
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Simulador Fresnel + Curvatura (pygame)")
clock = pygame.time.Clock()
font = pygame.font.SysFont(None, 20)
bigfont = pygame.font.SysFont(None, 28)

# Cores
WHITE=(255,255,255); BLACK=(0,0,0); GRAY=(160,160,160)
BLUE=(70,130,180); GREEN=(0,170,0); RED=(220,30,30); ORANGE=(245,140,0); BROWN=(110,70,40)

# ----------------- Física -----------------
def lamb(f_hz):  # comprimento de onda
    c = 3e8
    return c / f_hz

def fresnel_r1(x, D, lam):
    """ Raio da 1ª Fresnel ao longo do enlace (m) """
    if D <= 0: return 0.0
    return math.sqrt(max(0.0, lam * x * (D - x) / D))

def earth_bulge(x, D, R):
    """ Bojo da Terra relativo à corda TX-RX, em metros:
        b(x) = x(D-x) / (2 R_eff)
    """
    return (x * (D - x)) / (2.0 * R)

def to_screen_x(x_m, D):
    # m -> px (horizontal)
    return LEFT_PAD + int((x_m / D) * (WIDTH - LEFT_PAD - RIGHT_PAD))

def to_screen_y(height_m):
    # altura em metros acima do "nível base" -> y de tela
    base_line = HEIGHT - BOTTOM_PAD
    return int(base_line - (height_m / m_per_px))

def compute_clearance_60(D, lam, h_tx, h_rx, obs_x, obs_h, use_curv):
    """ Verifica a menor folga da LOS - 0.6*F1 contra terreno/obstáculo """
    N = 600
    worst_margin = 1e9
    hit_where = 0.0
    for i in range(N+1):
        x = D * i / N
        los_h = h_tx + (h_rx - h_tx) * (x / D)
        r1 = fresnel_r1(x, D, lam)
        need = los_h - 0.6 * r1  # limite inferior permitido

        ground = earth_bulge(x, D, R_eff) if use_curv else 0.0
        obst = 0.0
        if abs(x - obs_x) < 25.0:
            obst = obs_h + ground if use_curv else obs_h  # obstáculo sobre o solo
        blocker = max(ground, obst)

        margin = need - blocker
        if margin < worst_margin:
            worst_margin = margin
            hit_where = x
    return worst_margin, hit_where

# ----------------- Sliders -----------------
class Slider:
    def __init__(self, x, y, w, min_val, max_val, init_val, label, to_text=None):
        self.track = pygame.Rect(x, y, w, 6)
        self.min_val = min_val
        self.max_val = max_val
        self.value = init_val
        self.label = label
        self.knob_radius = 10
        self.dragging = False
        self.to_text = to_text  # função para formatar o valor no rótulo

    def _t_from_pos(self, px):
        px = min(max(px, self.track.left), self.track.right)
        return (px - self.track.left) / self.track.width

    def handle_event(self, event):
        if event.type == pygame.MOUSEBUTTONDOWN:
            # clicar no knob OU na trilha ativa arraste imediato
            if self.knob_rect().collidepoint(event.pos) or self.track.collidepoint(event.pos):
                self.dragging = True
                t = self._t_from_pos(event.pos[0])
                self.value = self.min_val + t * (self.max_val - self.min_val)
        elif event.type == pygame.MOUSEBUTTONUP:
            self.dragging = False
        elif event.type == pygame.MOUSEMOTION and self.dragging:
            t = self._t_from_pos(event.pos[0])
            self.value = self.min_val + t * (self.max_val - self.min_val)

    def knob_rect(self):
        t = (self.value - self.min_val) / (self.max_val - self.min_val)
        cx = self.track.left + int(t * self.track.width)
        cy = self.track.centery
        return pygame.Rect(cx - self.knob_radius, cy - self.knob_radius,
                           2*self.knob_radius, 2*self.knob_radius)

    def draw(self, surf):
        pygame.draw.rect(surf, GRAY, self.track)
        pygame.draw.circle(surf, BLUE, self.knob_rect().center, self.knob_radius)
        # rótulo
        if self.to_text:
            val_txt = self.to_text(self.value)
        else:
            val_txt = f"{self.value:.1f}"
        label = f"{self.label}: {val_txt}"
        surf.blit(font.render(label, True, BLACK),
                  (self.track.left, self.track.top - 20))

# Criar sliders:
# 1) Posição do obstáculo como FRAÇÃO (0..1) do enlace (exibimos em km no rótulo)
# 2) Escala vertical (m/px)
slider_obs_frac = Slider(
    x=LEFT_PAD, y=HEIGHT-90, w=400,
    min_val=0.0, max_val=1.0, init_val=obs_x / D_m,
    label="Posição obstáculo",
    to_text=lambda v: f"{(v*D_m)/1000:.2f} km"
)
slider_scale = Slider(
    x=LEFT_PAD+450, y=HEIGHT-90, w=300,
    min_val=1.0, max_val=200.0, init_val=m_per_px,
    label="Escala vertical (m/px)",
    to_text=lambda v: f"{v:.1f}"
)
sliders = [slider_obs_frac, slider_scale]

# ----------------- Desenho cena -----------------
def draw_scene():
    screen.fill(WHITE)

    lam = lamb(f_Hz)
    # Linha base
    pygame.draw.line(screen, GRAY, (LEFT_PAD, HEIGHT - BOTTOM_PAD),
                                  (WIDTH - RIGHT_PAD, HEIGHT - BOTTOM_PAD), 1)

    # Posições de tela para TX/RX
    tx_px = to_screen_x(0.0, D_m)
    rx_px = to_screen_x(D_m, D_m)
    tx_y = to_screen_y(h_tx)
    rx_y = to_screen_y(h_rx)

    # Curvatura (perfil do "chão")
    if show_curv:
        pts = []
        N = 300
        for i in range(N+1):
            x = D_m * i / N
            y_ground = earth_bulge(x, D_m, R_eff)
            pts.append((to_screen_x(x, D_m), to_screen_y(y_ground)))
        pygame.draw.lines(screen, BROWN, False, pts, 2)

    # LOS
    pygame.draw.line(screen, GREEN, (tx_px, tx_y), (rx_px, rx_y), 2)

    # Zona de Fresnel (polígono preenchido)
    if show_fresnel:
        top_pts = []
        bot_pts = []
        N = 300
        for i in range(N+1):
            x = D_m * i / N
            los_h = h_tx + (h_rx - h_tx) * (x / D_m)
            r1 = fresnel_r1(x, D_m, lam)
            top_pts.append((to_screen_x(x, D_m), to_screen_y(los_h + r1)))
            bot_pts.append((to_screen_x(x, D_m), to_screen_y(los_h - r1)))
        surf = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
        poly = top_pts + list(reversed(bot_pts))
        pygame.draw.polygon(surf, (100,170,220,90), poly)  # azul translúcido
        screen.blit(surf, (0,0))
        pygame.draw.lines(screen, BLUE, False, top_pts, 2)
        pygame.draw.lines(screen, BLUE, False, bot_pts, 2)

    # Antenas
    tower_w = 8
    pygame.draw.rect(screen, BLACK, (tx_px - tower_w//2, to_screen_y(0), tower_w, to_screen_y(0)-tx_y))
    pygame.draw.rect(screen, BLACK, (rx_px - tower_w//2, to_screen_y(0), tower_w, to_screen_y(0)-rx_y))
    pygame.draw.circle(screen, RED, (tx_px, tx_y), 6)
    pygame.draw.circle(screen, RED, (rx_px, rx_y), 6)

    # Obstáculo (retângulo)
    obs_px = to_screen_x(obs_x, D_m)
    ground_at_obs = earth_bulge(obs_x, D_m, R_eff) if show_curv else 0.0
    obs_top_y = to_screen_y(ground_at_obs + obs_h)
    obs_base_y = to_screen_y(ground_at_obs)
    pygame.draw.rect(screen, ORANGE, (obs_px-6, obs_top_y, 12, obs_base_y-obs_top_y))

    # Status (clearance 60% Fresnel)
    margin, where = compute_clearance_60(D_m, lam, h_tx, h_rx, obs_x, obs_h, show_curv)
    mid_r1 = fresnel_r1(D_m/2, D_m, lam)
    color = (0,140,0) if margin >= 0 else (200,30,30)
    msg1 = f"D={D_m/1000:.1f} km  f={f_Hz/1e9:.3f} GHz  λ={lam*100:.2f} cm"
    msg2 = f"TX={h_tx:.1f} m  RX={h_rx:.1f} m  Obs@{obs_x/1000:.2f} km h={obs_h:.1f} m"
    msg3 = f"F1@meio={mid_r1:.2f} m  (60%={0.6*mid_r1:.2f} m)  Escala: {m_per_px:.1f} m/px"
    msg4 = ("✅ 60% da 1ª Fresnel livre"
            if margin >= 0 else
            f"❌ Sem 60% Fresnel (falta {abs(margin):.2f} m)  @ x={where/1000:.2f} km")

    screen.blit(bigfont.render(msg1, True, BLACK), (LEFT_PAD, TOP_PAD - 40))
    screen.blit(bigfont.render(msg2, True, BLACK), (LEFT_PAD, TOP_PAD - 15))
    screen.blit(bigfont.render(msg3, True, BLACK), (LEFT_PAD, TOP_PAD + 10))
    screen.blit(bigfont.render(msg4, True, color), (LEFT_PAD, TOP_PAD + 35))

    # Legenda rápida (teclas ainda funcionam)
    help_lines = [
        "←/→ dist  ↑/↓ freq   W/S TX   E/D RX",
        "A/G obst.x   Z/X obst.h   C curva   F fresnel",
        "[ / ] escala vertical   R reset   (ou use os sliders abaixo)"
    ]
    base_help_y = HEIGHT - BOTTOM_PAD + 15
    for i, t in enumerate(help_lines):
        screen.blit(font.render(t, True, (70,70,70)), (LEFT_PAD, base_help_y + 18*i))

# ----------------- Reset -----------------
def reset_state():
    global D_m, f_Hz, h_tx, h_rx, obs_x, obs_h, show_curv, show_fresnel, m_per_px
    D_m = 50_000.0
    f_Hz = 2_000_000_000.0
    h_tx = 40.0
    h_rx = 35.0
    obs_x = D_m * 0.4
    obs_h = 20.0
    show_curv = True
    show_fresnel = True
    m_per_px = 10.0
    slider_obs_frac.value = obs_x / D_m
    slider_scale.value = m_per_px

# ----------------- Loop principal -----------------
def main():
    global D_m, f_Hz, h_tx, h_rx, obs_x, obs_h, show_curv, show_fresnel, m_per_px, R_eff
    running = True
    while running:
        dt = clock.tick(FPS)
        for e in pygame.event.get():
            if e.type == pygame.QUIT:
                running = False
            elif e.type == pygame.KEYDOWN:
                if e.key == pygame.K_ESCAPE: running = False
                # distância (km)
                elif e.key == pygame.K_LEFT:
                    D_m = max(1000.0, D_m - 1000.0)
                elif e.key == pygame.K_RIGHT:
                    D_m = min(200_000.0, D_m + 1000.0)
                # frequência
                elif e.key == pygame.K_UP:
                    f_Hz = min(20e9, f_Hz + 50e6)
                elif e.key == pygame.K_DOWN:
                    f_Hz = max(50e6, f_Hz - 50e6)
                # alturas
                elif e.key == pygame.K_w:
                    h_tx = min(500.0, h_tx + 1.0)
                elif e.key == pygame.K_s:
                    h_tx = max(0.0, h_tx - 1.0)
                elif e.key == pygame.K_e:
                    h_rx = min(500.0, h_rx + 1.0)
                elif e.key == pygame.K_d:
                    h_rx = max(0.0, h_rx - 1.0)
                # obstáculo horizontal pelas teclas (opcional)
                elif e.key == pygame.K_a:
                    obs_x = max(0.0, obs_x - 100.0)
                    slider_obs_frac.value = obs_x / D_m
                elif e.key == pygame.K_g:
                    obs_x = min(D_m, obs_x + 100.0)
                    slider_obs_frac.value = obs_x / D_m
                # obstáculo altura
                elif e.key == pygame.K_z:
                    obs_h = max(0.0, obs_h - 1.0)
                elif e.key == pygame.K_x:
                    obs_h = min(500.0, obs_h + 1.0)
                # Curvatura / Fresnel
                elif e.key == pygame.K_c:
                    show_curv = not show_curv
                elif e.key == pygame.K_f:
                    show_fresnel = not show_fresnel
                # Escala vertical via teclas
                elif e.key == pygame.K_LEFTBRACKET:   # '['
                    m_per_px = max(1.0, m_per_px - 1.0)
                    slider_scale.value = m_per_px
                elif e.key == pygame.K_RIGHTBRACKET:  # ']'
                    m_per_px = min(200.0, m_per_px + 1.0)
                    slider_scale.value = m_per_px
                # Reset
                elif e.key == pygame.K_r:
                    reset_state()

            # sliders com mouse
            for s in sliders:
                s.handle_event(e)

        # Atualizar var. ligadas aos sliders
        obs_x = slider_obs_frac.value * D_m
        m_per_px = slider_scale.value

        # manter R_eff coerente (se quiser variar K no futuro)
        R_eff = K * R_earth

        draw_scene()

        # desenhar sliders por cima
        for s in sliders:
            s.draw(screen)

        pygame.display.flip()

    pygame.quit()

if __name__ == "__main__":
    main()
