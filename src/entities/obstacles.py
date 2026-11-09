"""Obstáculos animados: causam dano ao tocar no jogador.

Dois comportamentos, para mostrar duas transformações diferentes:

  LaminaRotativa : fica no sítio e RODA (glRotate). Colisão por círculo,
                   porque o círculo não muda com a rotação.
  BarreiraLaser  : TRANSLADA-SE de um lado para o outro, com a posição
                   dada por um seno do tempo (movimento suave de vaivém,
                   abranda nas pontas como um pêndulo). Colisão AABB.

Ambas recebem um `multiplicador` (da onda) que as acelera.
Os inimigos atravessam-nas: só o jogador é afectado (decisão de design
para manter a IA simples).

zona_perigo() devolve a caixa que contém TODO o movimento do obstáculo;
serve para nunca fazer aparecer um cristal debaixo de uma lâmina.
"""

import math

from src.systems.collision import AABB, circulo_intersecta_aabb


class LaminaRotativa:

    def __init__(self, cx: float, cy: float, folha=None,
                 raio_visual: float = 56, raio_colisao: float = 40,
                 graus_por_segundo: float = 200):
        self.cx, self.cy = cx, cy
        self.folha = folha
        self.raio_visual = raio_visual
        # Mais pequeno que o desenho: as pontas das lâminas não magoam.
        # Jogos justos perdoam alguns píxeis ao jogador.
        self.raio_colisao = raio_colisao
        self.velocidade = graus_por_segundo
        self.angulo = 0.0

    def update(self, dt: float, multiplicador: float = 1.0) -> None:
        self.angulo = (self.angulo + self.velocidade * multiplicador * dt) % 360

    def toca(self, caixa: AABB) -> bool:
        return circulo_intersecta_aabb(self.cx, self.cy, self.raio_colisao, caixa)

    def zona_perigo(self) -> AABB:
        return AABB.a_partir_do_centro(self.cx, self.cy,
                                       self.raio_visual * 2, self.raio_visual * 2)

    def render(self, r) -> None:
        d = self.raio_visual * 2
        r.sprite(self.folha.textura, self.cx, self.cy, d, d, angulo=self.angulo)


class BarreiraLaser:

    def __init__(self, cy: float, x_min: float = 420, x_max: float = 860,
                 fase: float = 0.0, largura: float = 12, altura: float = 100,
                 periodo: float = 3.0):
        self.cy = cy
        self.x_min, self.x_max = x_min, x_max
        self.fase = fase
        self.largura, self.altura = largura, altura
        self.omega = 2 * math.pi / periodo     # velocidade angular do seno
        self.tempo = 0.0
        self.caixa = AABB(0, 0, largura, altura)
        self.update(0.0)

    def update(self, dt: float, multiplicador: float = 1.0) -> None:
        self.tempo += dt * multiplicador
        meio = (self.x_min + self.x_max) / 2
        amplitude = (self.x_max - self.x_min) / 2
        # x(t) = meio + A·sen(ωt + φ)  -> vaivém entre x_min e x_max
        cx = meio + amplitude * math.sin(self.omega * self.tempo + self.fase)
        self.caixa = AABB.a_partir_do_centro(cx, self.cy, self.largura, self.altura)

    def toca(self, caixa: AABB) -> bool:
        return self.caixa.intersecta(caixa)

    def zona_perigo(self) -> AABB:
        return AABB(self.x_min - self.largura, self.cy - self.altura / 2,
                    self.x_max - self.x_min + 2 * self.largura, self.altura)

    def render(self, r) -> None:
        cx, cy = self.caixa.centro
        brilho = 0.6 + 0.4 * math.sin(self.tempo * 20)       # cintila
        r.rect(cx, cy, self.largura * 3, self.altura + 8, (1.0, 0.2, 0.4, 0.25 * brilho))
        r.rect(cx, cy, self.largura, self.altura, (1.0, 0.35, 0.5, 0.9))
        r.rect(cx, cy, self.largura / 3, self.altura, (1.0, 0.9, 0.95, 1.0))
        # Emissores nas pontas
        r.rect(cx, cy - self.altura / 2, 20, 8, (0.5, 0.5, 0.6, 1))
        r.rect(cx, cy + self.altura / 2, 20, 8, (0.5, 0.5, 0.6, 1))
