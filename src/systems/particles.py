"""Sistema de partículas: pequenos quadrados que explodem e desvanecem.

Cada partícula tem posição, velocidade, cor e tempo de vida. Em cada frame:
    posição  += velocidade · dt          (movimento)
    velocidade *= atrito                 (abranda)
    alfa e tamanho = proporcionais à vida que resta  (desvanece e encolhe)
Quando a vida chega a 0, a partícula é removida.

É um efeito visual barato e muito expressivo: 20 quadrados coloridos a
espalharem-se tornam "apanhar um cristal" muito mais satisfatório.
"""

import math
import random
from dataclasses import dataclass


@dataclass
class Particula:
    x: float
    y: float
    vx: float
    vy: float
    vida: float
    vida_total: float
    cor: tuple
    tamanho: float


class SistemaParticulas:

    ATRITO_POR_SEGUNDO = 0.04    # fracção da velocidade que sobra após 1 s
    LIMITE = 600                 # segurança: nunca mais do que isto

    def __init__(self, rng: random.Random | None = None):
        self.rng = rng or random.Random()
        self.particulas: list[Particula] = []

    def emitir(self, x: float, y: float, quantidade: int, cor,
               velocidade: float = 220, vida: float = 0.6, tamanho: float = 8) -> None:
        for _ in range(quantidade):
            angulo = self.rng.uniform(0, 2 * math.pi)        # direcção aleatória
            v = velocidade * self.rng.uniform(0.3, 1.0)
            duracao = vida * self.rng.uniform(0.6, 1.0)
            self.particulas.append(Particula(
                x, y, math.cos(angulo) * v, math.sin(angulo) * v,
                duracao, duracao, cor, tamanho * self.rng.uniform(0.6, 1.2)))
        del self.particulas[:-self.LIMITE]                   # descarta as mais antigas

    def update(self, dt: float) -> None:
        atrito = self.ATRITO_POR_SEGUNDO ** dt      # independente do FPS
        vivas = []
        for p in self.particulas:
            p.vida -= dt
            if p.vida <= 0:
                continue
            p.x += p.vx * dt
            p.y += p.vy * dt
            p.vx *= atrito
            p.vy *= atrito
            vivas.append(p)
        self.particulas = vivas

    def render(self, r) -> None:
        for p in self.particulas:
            f = p.vida / p.vida_total               # 1 -> 0 ao longo da vida
            cr, cg, cb, ca = p.cor
            r.rect(p.x, p.y, p.tamanho * f, p.tamanho * f, (cr, cg, cb, ca * f))
