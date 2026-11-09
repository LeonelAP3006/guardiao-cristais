"""Sentinela: inimigo controlado pela IA (systems/ai.py).

Divisão de responsabilidades:
  ControladorIA -> DECIDE para onde ir e a que velocidade (o "cérebro")
  Sentinela     -> MOVE-SE com colisão, anima-se e desenha-se (o "corpo")
Se quiséssemos um 2.º tipo de inimigo (mais rápido, mais atento), bastava
criar outro ControladorIA com outros parâmetros; o corpo era o mesmo.
"""

import math

from src import config
from src.systems.ai import PERSEGUICAO, ControladorIA
from src.systems.animation import Animation, Animator
from src.systems.collision import AABB, mover_com_colisao

FORCA_SEPARACAO = 120.0      # unidades/s com que dois inimigos se afastam

COR_RAIO_PATRULHA = (0.3, 0.6, 1.0, 0.10)


def separar_inimigos(inimigos: list["Sentinela"], paredes: list[AABB], dt: float) -> None:
    """Regra de SEPARAÇÃO (comportamento de grupo, tipo "boids").

    Sem ela, várias sentinelas a perseguir o mesmo jogador acabam
    exactamente no mesmo sítio e parecem uma só. Para cada par que se
    sobrepõe, empurramo-las em sentidos opostos, ao longo da linha que
    une os centros. O empurrão usa mover_com_colisao, por isso nunca
    atira um inimigo para dentro de uma parede.
    """
    passo = FORCA_SEPARACAO * dt
    for i, a in enumerate(inimigos):
        for b in inimigos[i + 1:]:
            if not a.caixa.intersecta(b.caixa):
                continue
            (ax, ay), (bx, by) = a.posicao, b.posicao
            dx, dy = ax - bx, ay - by
            d = math.hypot(dx, dy)
            if d < 1e-6:                       # exactamente sobrepostos
                dx, dy, d = 1.0, 0.0, 1.0      # escolher um eixo qualquer
            ux, uy = dx / d * passo, dy / d * passo
            mover_com_colisao(a.caixa, ux, uy, paredes)
            mover_com_colisao(b.caixa, -ux, -uy, paredes)
COR_RAIO_ALERTA = (1.0, 0.25, 0.25, 0.16)


class Sentinela:

    def __init__(self, rota: list[tuple[float, float]], folha=None):
        cx, cy = rota[0]
        self.caixa = AABB.a_partir_do_centro(cx, cy, *config.INIMIGO_HITBOX)
        self.ia = ControladorIA(rota)
        self.rota = rota
        self.folha = folha
        self.olha_esquerda = False
        # Frames de sentinela.png: 0-1 patrulha (olho azul), 2-3 alerta (olho vermelho)
        self.animator = Animator({
            "patrulha": Animation([0, 1], 0.30),
            "alerta": Animation([2, 3], 0.10),
        }, inicial="patrulha")

    @property
    def posicao(self):
        return self.caixa.centro

    @property
    def em_alerta(self) -> bool:
        return self.ia.estado == PERSEGUICAO

    def update(self, dt: float, pos_jogador, paredes: list[AABB],
               multiplicador: float = 1.0) -> None:
        dx, dy, vel = self.ia.decidir(dt, self.posicao, pos_jogador, paredes, multiplicador)
        # Mesma colisão que o jogador: desliza pelas paredes e contorna pilares.
        mover_com_colisao(self.caixa, dx * vel * dt, dy * vel * dt, paredes)
        if abs(dx) > 0.1:
            self.olha_esquerda = dx < 0
        self.animator.tocar("alerta" if self.em_alerta else "patrulha")
        self.animator.update(dt)

    def render(self, r) -> None:
        cx, cy = self.posicao
        tamanho = config.TAMANHO_FRAME * config.ESCALA_SPRITE
        r.sprite(self.folha.textura, cx, cy - 6, tamanho, tamanho,
                 uv=self.folha.uv(self.animator.frame),
                 espelhar_x=self.olha_esquerda)

    def render_debug(self, r) -> None:
        """Raio de detecção (F1): azul a patrulhar, vermelho a perseguir."""
        cor = COR_RAIO_ALERTA if self.em_alerta else COR_RAIO_PATRULHA
        r.circulo(*self.posicao, self.ia.raio, cor)
        if self.em_alerta and self.ia.ultima_vista:
            r.circulo(*self.ia.ultima_vista, 6, (1, 0.3, 0.3, 0.9))
