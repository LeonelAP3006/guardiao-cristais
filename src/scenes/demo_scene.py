"""Cena de VALIDAÇÃO do Bloco 1 (será substituída pela PlayScene no Bloco 2).

Serve para provar, à frente de toda a equipa, que a base gráfica funciona:
  - círculo no centro          -> janela-visor sem distorção (redimensionar!)
  - lâminas a rodar e pulsar   -> transformações: rotação, escala, translação
  - explorador animado         -> textura + spritesheet + animação por frames
  - setas/WASD                 -> teclado, movimento com delta time
  - clique do rato             -> rato convertido para coordenadas do mundo
"""

import math
import os

import pygame

from src import config
from src.engine.renderer import Renderer
from src.engine.texture import SpriteSheet, Texture
from src.engine.window import janela_para_mundo

VELOCIDADE_DEMO = 300.0        # unidades do mundo por segundo
DURACAO_FRAME = 0.12           # segundos que cada frame da animação fica visível
TAMANHO_SPRITE = 96            # o sprite tem 32 px, desenhamos ampliado 3x


class DemoScene:

    def __init__(self, game_ref=None):
        self.game = game_ref
        caminho = os.path.join(config.PASTA_ASSETS, "sprites", "explorador.png")
        self.folha = SpriteSheet(Texture.carregar(caminho), 32, 32)

        self.x = config.MUNDO_LARGURA * 0.25
        self.y = config.MUNDO_ALTURA * 0.5
        self.olha_esquerda = False
        self.a_mover = False

        self.tempo = 0.0              # tempo total decorrido (para as animações)
        self.tempo_frame = 0.0
        self.frame = 0
        self.marcas: list[tuple[float, float]] = []   # cliques do rato

    # -- eventos --------------------------------------------------------------
    def handle_event(self, evento) -> None:
        if evento.type == pygame.KEYDOWN and evento.key == pygame.K_ESCAPE:
            if self.game:
                self.game.parar()
        elif evento.type == pygame.MOUSEBUTTONDOWN and evento.button == 1:
            # evento.pos vem em píxeis da JANELA; convertemos para o MUNDO.
            mx, my = janela_para_mundo(*evento.pos, self.game.window.viewport)
            self.marcas = (self.marcas + [(mx, my)])[-8:]

    # -- lógica ---------------------------------------------------------------
    def update(self, dt: float) -> None:
        self.tempo += dt

        teclas = pygame.key.get_pressed()
        dx = (teclas[pygame.K_RIGHT] or teclas[pygame.K_d]) - (teclas[pygame.K_LEFT] or teclas[pygame.K_a])
        dy = (teclas[pygame.K_DOWN] or teclas[pygame.K_s]) - (teclas[pygame.K_UP] or teclas[pygame.K_w])

        self.a_mover = dx != 0 or dy != 0
        if self.a_mover:
            # Normalizar: sem isto, na diagonal (1,1) o comprimento seria
            # sqrt(2) ~ 1.41 e o personagem andaria 41% mais depressa.
            comprimento = math.hypot(dx, dy)
            dx, dy = dx / comprimento, dy / comprimento
            # distância = velocidade x tempo. Com dt, 1 segundo de tecla
            # premida move 300 unidades, quer o jogo corra a 30 ou a 144 FPS.
            self.x += dx * VELOCIDADE_DEMO * dt
            self.y += dy * VELOCIDADE_DEMO * dt
            if dx:
                self.olha_esquerda = dx < 0

        # Limites do mundo (o sprite não sai do ecrã).
        meio = TAMANHO_SPRITE / 2
        self.x = max(meio, min(config.MUNDO_LARGURA - meio, self.x))
        self.y = max(meio, min(config.MUNDO_ALTURA - meio, self.y))

        # Animação: frames 0-1 = parado (respirar), 2-5 = a andar.
        self.tempo_frame += dt
        if self.tempo_frame >= DURACAO_FRAME:
            self.tempo_frame -= DURACAO_FRAME
            self.frame += 1

    # -- desenho --------------------------------------------------------------
    def render(self, r: Renderer) -> None:
        cx, cy = config.MUNDO_LARGURA / 2, config.MUNDO_ALTURA / 2

        # Círculo de teste de proporção.
        r.circulo(cx, cy, 150, (0.20, 0.24, 0.36, 1.0))
        r.circulo(cx, cy, 8, (0.9, 0.9, 1.0, 1.0))

        # Lâmina: ROTAÇÃO contínua em torno do próprio centro (90 graus/s).
        r.rect(cx, cy, 260, 18, (0.85, 0.30, 0.30, 1.0), angulo=self.tempo * 90)
        # Segunda lâmina: rotação inversa + ESCALA a pulsar (seno do tempo).
        pulso = 1.0 + 0.25 * math.sin(self.tempo * 3)
        r.rect(cx + 400, cy, 120 * pulso, 120 * pulso,
               (0.30, 0.75, 0.55, 1.0), angulo=-self.tempo * 60)
        # TRANSLAÇÃO oscilante (barreira que vai e vem).
        r.rect(cx, 80 + 40 * math.sin(self.tempo * 2), 600, 16, (0.95, 0.75, 0.25, 1.0))

        # Marcas dos cliques do rato.
        for mx, my in self.marcas:
            r.circulo(mx, my, 10, (0.4, 0.8, 1.0, 0.8))

        # Explorador animado (spritesheet).
        if self.a_mover:
            indice = 2 + self.frame % 4
        else:
            indice = self.frame // 3 % 2
        r.sprite(self.folha.textura, self.x, self.y, TAMANHO_SPRITE, TAMANHO_SPRITE,
                 uv=self.folha.uv(indice), espelhar_x=self.olha_esquerda)
