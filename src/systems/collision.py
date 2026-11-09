"""Sistema de colisão AABB (Axis-Aligned Bounding Box).

Uma AABB é um rectângulo com os lados paralelos aos eixos X e Y.
Dois rectângulos destes tocam-se se, e só se, se sobrepõem NOS DOIS EIXOS:

      A.esquerda < B.direita   e   A.direita > B.esquerda    (eixo X)
      A.topo     < B.fundo     e   A.fundo   > B.topo        (eixo Y)

Basta UMA destas desigualdades falhar para haver um "corredor" entre eles.
Usamos < e > (estritos): encostar exactamente à parede NÃO é colisão,
senão o jogador ficava "colado" ao parar junto a uma parede.

Porquê AABB e não círculos ou polígonos?
  - Paredes, sprites e hitboxes são rectângulos alinhados: encaixe natural.
  - 4 comparações, sem raízes quadradas nem trigonometria.
  - Limitação: objectos rodados (ex.: lâmina rotativa) não são AABB.
    Para esses usaremos círculo (Bloco 3), que não muda ao rodar.

Este módulo é PURO (não usa OpenGL nem Pygame): é testado em tests/.
"""

import math
from dataclasses import dataclass


@dataclass
class AABB:
    """Rectângulo definido pelo canto superior esquerdo (x, y), largura e altura."""
    x: float
    y: float
    w: float
    h: float

    # -- propriedades de leitura ----------------------------------------------
    @property
    def esquerda(self) -> float:
        return self.x

    @property
    def direita(self) -> float:
        return self.x + self.w

    @property
    def topo(self) -> float:
        return self.y

    @property
    def fundo(self) -> float:
        return self.y + self.h

    @property
    def centro(self) -> tuple[float, float]:
        return self.x + self.w / 2, self.y + self.h / 2

    @classmethod
    def a_partir_do_centro(cls, cx: float, cy: float, w: float, h: float) -> "AABB":
        return cls(cx - w / 2, cy - h / 2, w, h)

    # -- testes -----------------------------------------------------------------
    def intersecta(self, outra: "AABB") -> bool:
        return (self.esquerda < outra.direita and self.direita > outra.esquerda and
                self.topo < outra.fundo and self.fundo > outra.topo)

    def contem(self, px: float, py: float) -> bool:
        return self.esquerda <= px <= self.direita and self.topo <= py <= self.fundo


def circulo_intersecta_aabb(cx: float, cy: float, raio: float, caixa: AABB) -> bool:
    """Colisão círculo-rectângulo (usada nas lâminas rotativas).

    Porquê círculo para a lâmina? Ela RODA. Uma AABB não roda (é sempre
    alinhada aos eixos), mas um círculo é igual em qualquer ângulo.

    Algoritmo do "ponto mais próximo":
      1. Encontrar o ponto do rectângulo mais próximo do centro do círculo,
         prendendo (clamp) cx e cy aos limites do rectângulo.
      2. Há colisão se esse ponto estiver a menos de `raio` do centro.
    Comparamos distâncias AO QUADRADO para evitar a raiz quadrada.
    """
    px = max(caixa.esquerda, min(cx, caixa.direita))
    py = max(caixa.topo, min(cy, caixa.fundo))
    return (cx - px) ** 2 + (cy - py) ** 2 < raio ** 2


def linha_de_visao(a: tuple[float, float], b: tuple[float, float],
                   solidos: list[AABB], passo: float = 10.0) -> bool:
    """True se o segmento de A até B não atravessa nenhum sólido.

    Método simples por AMOSTRAGEM: percorremos o segmento em pontos
    espaçados de `passo` unidades e verificamos se algum cai dentro de
    uma parede. Com passo 10 e paredes de 32+ de espessura, nenhuma
    parede escapa. É o que permite ao inimigo "não ver" através de pilares.
    """
    (ax, ay), (bx, by) = a, b
    distancia = math.hypot(bx - ax, by - ay)
    n = max(1, int(distancia / passo))
    for i in range(1, n):
        t = i / n
        px, py = ax + (bx - ax) * t, ay + (by - ay) * t
        if any(s.contem(px, py) for s in solidos):
            return False
    return True


def mover_com_colisao(caixa: AABB, dx: float, dy: float,
                      solidos: list[AABB]) -> tuple[bool, bool]:
    """Move `caixa` por (dx, dy) sem entrar em nenhum sólido. Altera `caixa`.

    Algoritmo: resolução SEPARADA POR EIXO.
      1. Mover só em X. Se bater num sólido, encostar à face dele.
      2. Depois mover só em Y. Se bater, encostar.
    Porquê separar? Se movêssemos na diagonal e, ao bater, cancelássemos
    tudo, o jogador "colava" à parede. Separando, quando anda na diagonal
    contra uma parede vertical, o X é bloqueado mas o Y continua:
    o jogador DESLIZA ao longo da parede, como em qualquer jogo clássico.

    Devolve (bateu_em_x, bateu_em_y), útil para animações ou IA.

    Limitação conhecida (tunelling): se num só frame o deslocamento for maior
    do que a espessura de uma parede, a caixa pode saltá-la. Com
    DT_MAXIMO = 0.05 s e velocidades < 400/s, o passo máximo é 20 unidades,
    menor do que a parede (32). Ver config.py.
    """
    bateu_x = bateu_y = False

    caixa.x += dx
    for s in solidos:
        if caixa.intersecta(s):
            bateu_x = True
            if dx > 0:
                caixa.x = s.esquerda - caixa.w     # vinha da esquerda
            elif dx < 0:
                caixa.x = s.direita                # vinha da direita

    caixa.y += dy
    for s in solidos:
        if caixa.intersecta(s):
            bateu_y = True
            if dy > 0:
                caixa.y = s.topo - caixa.h         # vinha de cima
            elif dy < 0:
                caixa.y = s.fundo                  # vinha de baixo

    return bateu_x, bateu_y
