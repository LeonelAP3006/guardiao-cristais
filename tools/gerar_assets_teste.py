"""Gera assets PROVISÓRIOS (criados por nós, sem direitos de terceiros).

  assets/sprites/explorador.png : spritesheet 6 frames de 32x32
        frames 0-1 parado (respira), frames 2-5 a andar
  assets/sprites/parede.png     : ladrilho de tijolos 32x32 (repetível)
  assets/sprites/sentinela.png  : inimigo, 4 frames (patrulha / alerta)
  assets/sprites/cristal.png    : cristal, 4 frames de brilho
  assets/sprites/lamina.png     : lâmina de 4 pontas (rodada pelo OpenGL)
  assets/sprites/coracao.png    : ícone de vida 16x16
  assets/sprites/powerups.png   : escudo, velocidade, vida (3 frames)
Os sons e a música são gerados por tools/gerar_sons.py.
  assets/sounds/teste.wav       : bip de 0,3 s para validar o áudio

Executar uma vez:  python tools/gerar_assets_teste.py
Mais tarde substituímos por arte CC0 (ex.: Kenney.nl) com o mesmo formato.
"""

import math
import os
import struct
import wave

os.environ.setdefault("SDL_VIDEODRIVER", "dummy")   # não abre janela
import pygame  # noqa: E402

RAIZ = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
F = 32  # tamanho de cada frame

PELE = (240, 200, 160)
CHAPEU = (150, 95, 45)
CAMISA = (60, 140, 200)
CALCAS = (60, 60, 90)
BOTAS = (50, 35, 25)
OLHO = (20, 20, 30)


def desenhar_frame(s: pygame.Surface, ox: int, perna: int, respira: int) -> None:
    """Desenha um explorador de perfil (a olhar para a direita) no frame ox."""
    y = respira  # 0 ou 1 píxel para baixo -> efeito de respiração
    # chapéu
    pygame.draw.rect(s, CHAPEU, (ox + 9, 3 + y, 14, 4))
    pygame.draw.rect(s, CHAPEU, (ox + 7, 7 + y, 19, 2))
    # cabeça e olho
    pygame.draw.rect(s, PELE, (ox + 10, 9 + y, 12, 7))
    pygame.draw.rect(s, OLHO, (ox + 18, 11 + y, 2, 2))
    # tronco
    pygame.draw.rect(s, CAMISA, (ox + 10, 16 + y, 12, 8))
    # braço que balança com as pernas
    pygame.draw.rect(s, PELE, (ox + 14 - perna // 2, 18 + y, 3, 5))
    # pernas: perna em -2..2 afasta-as
    pygame.draw.rect(s, CALCAS, (ox + 11 + perna, 24, 4, 5))
    pygame.draw.rect(s, CALCAS, (ox + 17 - perna, 24, 4, 5))
    pygame.draw.rect(s, BOTAS, (ox + 11 + perna, 29, 5, 2))
    pygame.draw.rect(s, BOTAS, (ox + 17 - perna, 29, 5, 2))


def gerar_spritesheet() -> str:
    folha = pygame.Surface((F * 6, F), pygame.SRCALPHA)
    folha.fill((0, 0, 0, 0))  # fundo transparente
    desenhar_frame(folha, 0 * F, 0, 0)      # parado
    desenhar_frame(folha, 1 * F, 0, 1)      # parado (respira)
    for i, perna in enumerate((2, 0, -2, 0)):
        desenhar_frame(folha, (2 + i) * F, perna, 0)
    caminho = os.path.join(RAIZ, "assets", "sprites", "explorador.png")
    os.makedirs(os.path.dirname(caminho), exist_ok=True)
    pygame.image.save(folha, caminho)
    return caminho


def gerar_parede() -> str:
    """Ladrilho de tijolos 32x32 que encaixa consigo próprio (para GL_REPEAT)."""
    s = pygame.Surface((F, F), pygame.SRCALPHA)
    s.fill((70, 62, 88, 255))                 # argamassa
    tijolo, sombra, luz = (120, 96, 140), (96, 76, 114), (150, 126, 170)
    # 2 fiadas de 16 px; a 2.ª desfasada meio tijolo -> o padrão continua
    # sem costura quando o ladrilho é repetido lado a lado.
    for linha, desfase in ((0, 0), (1, 8)):
        y = linha * 16
        for x in range(-16 + desfase, F, 16):
            pygame.draw.rect(s, tijolo, (x + 1, y + 1, 14, 14))
            pygame.draw.rect(s, luz, (x + 1, y + 1, 14, 2))
            pygame.draw.rect(s, sombra, (x + 1, y + 13, 14, 2))
    caminho = os.path.join(RAIZ, "assets", "sprites", "parede.png")
    pygame.image.save(s, caminho)
    return caminho


def _guardar(surface: pygame.Surface, nome: str) -> str:
    caminho = os.path.join(RAIZ, "assets", "sprites", nome)
    pygame.image.save(surface, caminho)
    return caminho


def gerar_sentinela() -> str:
    """Robô sentinela, 4 frames: 0-1 patrulha (olho azul), 2-3 alerta (vermelho)."""
    folha = pygame.Surface((F * 4, F), pygame.SRCALPHA)
    metal, escuro, claro = (120, 128, 150), (70, 76, 96), (170, 178, 200)
    for i in range(4):
        ox = i * F
        alerta = i >= 2
        sobe = i % 2                                  # balança 1 px
        olho = (255, 70, 70) if alerta else (90, 200, 255)
        # antena com luz
        pygame.draw.rect(folha, escuro, (ox + 15, 3 + sobe, 2, 5))
        pygame.draw.rect(folha, olho if (alerta and i == 2) or not alerta else claro,
                         (ox + 14, 2 + sobe, 4, 3))
        # cabeça/corpo em cúpula
        pygame.draw.ellipse(folha, metal, (ox + 6, 7 + sobe, 20, 18))
        pygame.draw.ellipse(folha, claro, (ox + 9, 9 + sobe, 8, 5))
        pygame.draw.rect(folha, escuro, (ox + 6, 18 + sobe, 20, 6))
        # visor e olho (o olho pisca/varre na patrulha)
        pygame.draw.rect(folha, (25, 25, 35), (ox + 9, 12 + sobe, 14, 5))
        ox_olho = ox + (17 if alerta else 12 + 4 * sobe)
        pygame.draw.rect(folha, olho, (ox_olho, 13 + sobe, 4, 3))
        # pernas
        p = 1 if sobe else 0
        pygame.draw.rect(folha, escuro, (ox + 9 - p, 24, 4, 5))
        pygame.draw.rect(folha, escuro, (ox + 19 + p, 24, 4, 5))
        pygame.draw.rect(folha, (40, 40, 50), (ox + 8 - p, 28, 6, 2))
        pygame.draw.rect(folha, (40, 40, 50), (ox + 18 + p, 28, 6, 2))
    return _guardar(folha, "sentinela.png")


def gerar_cristal() -> str:
    """Cristal com um brilho branco que o percorre (4 frames)."""
    folha = pygame.Surface((F * 4, F), pygame.SRCALPHA)
    for i in range(4):
        ox = i * F
        topo, meio_e, meio_d, base = (ox + 16, 3), (ox + 6, 13), (ox + 26, 13), (ox + 16, 29)
        pygame.draw.polygon(folha, (40, 170, 220), [topo, meio_e, base, meio_d])
        pygame.draw.polygon(folha, (110, 230, 255), [topo, meio_e, (ox + 16, 13)])
        pygame.draw.polygon(folha, (20, 120, 180), [(ox + 16, 13), meio_d, base])
        pygame.draw.polygon(folha, (210, 250, 255), [topo, meio_e, base, meio_d], 1)
        by = 6 + i * 5                                 # brilho desce frame a frame
        pygame.draw.rect(folha, (255, 255, 255), (ox + 13, by, 3, 3))
    return _guardar(folha, "cristal.png")


def gerar_lamina() -> str:
    """Lâmina de 4 pontas. Desenhada direita; a rotação é feita pelo OpenGL."""
    s = pygame.Surface((F, F), pygame.SRCALPHA)
    c = 16
    for dx, dy, px, py in ((0, -1, 1, 0), (1, 0, 0, 1), (0, 1, -1, 0), (-1, 0, 0, -1)):
        ponta = (c + dx * 15, c + dy * 15)
        lado = (c + px * 6 + dx * 3, c + py * 6 + dy * 3)
        pygame.draw.polygon(s, (190, 195, 210), [(c, c), lado, ponta])
        pygame.draw.polygon(s, (230, 235, 245), [(c, c), lado, ponta], 1)
    pygame.draw.circle(s, (180, 40, 50), (c, c), 5)
    pygame.draw.circle(s, (60, 60, 70), (c, c), 2)
    return _guardar(s, "lamina.png")


def gerar_coracao() -> str:
    s = pygame.Surface((16, 16), pygame.SRCALPHA)
    pygame.draw.circle(s, (230, 50, 70), (5, 6), 4)
    pygame.draw.circle(s, (230, 50, 70), (11, 6), 4)
    pygame.draw.polygon(s, (230, 50, 70), [(1, 7), (15, 7), (8, 15)])
    pygame.draw.rect(s, (255, 170, 180), (4, 4, 2, 2))
    return _guardar(s, "coracao.png")


def gerar_powerups() -> str:
    """3 frames 32x32: escudo (azul), velocidade (amarelo), vida (vermelho)."""
    folha = pygame.Surface((F * 3, F), pygame.SRCALPHA)
    cores = [(70, 190, 255), (255, 210, 60), (240, 70, 90)]
    for i, cor in enumerate(cores):
        ox, c = i * F, i * F + 16
        escura = tuple(int(v * 0.55) for v in cor)
        pygame.draw.circle(folha, escura, (c, 16), 15)          # medalha
        pygame.draw.circle(folha, cor, (c, 16), 15, 2)
        branco = (255, 255, 255)
        if i == 0:      # escudo
            pygame.draw.polygon(folha, branco, [(c - 8, 8), (c + 8, 8), (c + 8, 16), (c, 25), (c - 8, 16)])
            pygame.draw.polygon(folha, cor, [(c - 5, 11), (c + 5, 11), (c + 5, 16), (c, 21), (c - 5, 16)])
        elif i == 1:    # raio
            pygame.draw.polygon(folha, branco, [(c + 3, 5), (c - 7, 18), (c - 1, 18),
                                                (c - 3, 27), (c + 7, 13), (c + 1, 13)])
        else:           # coração com +
            pygame.draw.circle(folha, branco, (c - 4, 13), 5)
            pygame.draw.circle(folha, branco, (c + 4, 13), 5)
            pygame.draw.polygon(folha, branco, [(c - 9, 15), (c + 9, 15), (c, 25)])
            pygame.draw.rect(folha, cor, (c - 1, 10, 3, 9))
            pygame.draw.rect(folha, cor, (c - 4, 13, 9, 3))
        pygame.draw.rect(folha, (255, 255, 255), (ox + 9, 6, 3, 2))   # reflexo
    return _guardar(folha, "powerups.png")


def gerar_bip() -> str:
    caminho = os.path.join(RAIZ, "assets", "sounds", "teste.wav")
    os.makedirs(os.path.dirname(caminho), exist_ok=True)
    taxa, dur, freq = 44100, 0.3, 880
    with wave.open(caminho, "wb") as w:
        w.setnchannels(1)
        w.setsampwidth(2)
        w.setframerate(taxa)
        n = int(taxa * dur)
        amostras = (
            int(12000 * math.sin(2 * math.pi * freq * i / taxa) * (1 - i / n))
            for i in range(n)
        )
        w.writeframes(b"".join(struct.pack("<h", a) for a in amostras))
    return caminho


if __name__ == "__main__":
    pygame.init()
    print("Criado:", gerar_spritesheet())
    print("Criado:", gerar_parede())
    for gerar in (gerar_sentinela, gerar_cristal, gerar_lamina, gerar_coracao,
                  gerar_powerups):
        print("Criado:", gerar())
    print("Criado:", gerar_bip())
    pygame.quit()
