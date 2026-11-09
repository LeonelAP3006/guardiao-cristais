"""A arena: as paredes sólidas onde o jogo decorre.

A disposição é DADOS (uma lista de rectângulos), separada do desenho.
A função criar_paredes() não usa OpenGL, por isso os testes conseguem
verificar, por exemplo, que o ponto de partida do jogador está livre.
"""

from src import config
from src.systems.collision import AABB

PONTO_INICIAL = (config.MUNDO_LARGURA / 2, config.MUNDO_ALTURA / 2)

# Rotas de patrulha das sentinelas (pontos por onde passam, em ciclo).
# Todas ficam longe do ponto inicial do jogador e em corredores livres.
ROTAS_PATRULHA = [
    [(120, 100), (470, 100), (470, 300), (120, 300)],      # canto sup. esq.
    [(1160, 620), (810, 620), (810, 420), (1160, 420)],    # canto inf. dir.
    [(1160, 100), (810, 100), (810, 300), (1160, 300)],    # canto sup. dir.
    [(120, 620), (470, 620), (470, 420), (120, 420)],      # canto inf. esq.
    [(380, 85), (900, 85)],                                # corredor de cima
    [(380, 635), (900, 635)],                              # corredor de baixo
]

# Obstáculos animados: (cx, cy) das lâminas; lasers (y, fase).
LAMINAS = [(360, 360), (920, 360)]
LASERS = [(250, 0.0), (470, 3.14159)]


def criar_paredes() -> list[AABB]:
    W, H, t = config.MUNDO_LARGURA, config.MUNDO_ALTURA, config.ESPESSURA_PAREDE
    return [
        # Contorno: impede o jogador de sair do mundo
        AABB(0, 0, W, t),                 # cima
        AABB(0, H - t, W, t),             # baixo
        AABB(0, t, t, H - 2 * t),         # esquerda
        AABB(W - t, t, t, H - 2 * t),     # direita
        # Pilares: obrigam o jogador (e, mais tarde, os inimigos) a contornar
        AABB(256, 160, 64, 64),
        AABB(960, 160, 64, 64),
        AABB(256, 496, 64, 64),
        AABB(960, 496, 64, 64),
        # Barras perto do topo e do fundo; o centro fica livre
        AABB(544, 128, 192, 32),
        AABB(544, 560, 192, 32),
    ]


class Arena:

    def __init__(self, textura_parede=None):
        self.paredes = criar_paredes()
        self.textura = textura_parede      # textura com repetir=True

    def render(self, r) -> None:
        lado = self.textura.largura        # 1 ladrilho = 32 unidades de mundo
        for p in self.paredes:
            cx, cy = p.centro
            # UV maior que 1 + GL_REPEAT = a textura repete-se em mosaico.
            # Uma parede de 192x32 usa u de 0 a 6: 6 ladrilhos na horizontal.
            r.sprite(self.textura, cx, cy, p.w, p.h,
                     uv=(0.0, 0.0, p.w / lado, p.h / lado))
