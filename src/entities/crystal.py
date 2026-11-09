"""Cristal: o objecto que o jogador recolhe para pontuar."""

import math

from src import config
from src.systems.animation import Animation
from src.systems.collision import AABB


class Cristal:

    def __init__(self, cx: float, cy: float, folha=None):
        t = config.CRISTAL_TAMANHO
        self.caixa = AABB.a_partir_do_centro(cx, cy, t, t)
        self.folha = folha
        self.animacao = Animation([0, 1, 2, 3], 0.12)   # brilho a percorrer o cristal
        self.tempo = 0.0

    def mover_para(self, cx: float, cy: float) -> None:
        """Reaproveitamos o mesmo objecto em vez de criar um novo."""
        t = config.CRISTAL_TAMANHO
        self.caixa = AABB.a_partir_do_centro(cx, cy, t, t)

    def update(self, dt: float) -> None:
        self.tempo += dt
        self.animacao.update(dt)

    def render(self, r) -> None:
        cx, cy = self.caixa.centro
        # Translação vertical em seno: o cristal "flutua" (só no desenho;
        # a hitbox não se mexe, para a colisão ser previsível).
        flutuar = 4 * math.sin(self.tempo * 4)
        tamanho = config.TAMANHO_FRAME * 2
        r.sprite(self.folha.textura, cx, cy + flutuar, tamanho, tamanho,
                 uv=self.folha.uv(self.animacao.frame))
