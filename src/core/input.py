"""Gestor de input: teclado e rato, traduzidos em ACÇÕES do jogo.

Há dois tipos de pergunta que o jogo faz ao teclado:
  - "está premida?"       (segurar)  -> movimento contínuo, usa a ACÇÃO "cima"...
  - "foi premida AGORA?"  (carregar) -> pausar, confirmar no menu, F1
Se usássemos "está premida" para a pausa, segurar ESC por meio segundo
pausava e despausava 30 vezes. Por isso guardamos os KEYDOWN deste frame.

O Game chama inicio_frame() uma vez por frame e processar(evento) para cada
evento. As cenas só fazem perguntas: segurada(), carregada(), direccao(), ...
"""

import math

import pygame

from src import config
from src.engine.window import janela_para_mundo


def vector_direccao(esquerda: bool, direita: bool,
                    cima: bool, baixo: bool) -> tuple[float, float]:
    """Direcção pedida pelas teclas, com comprimento 1 (ou (0, 0)).

    Sem normalizar, na diagonal o vector seria (1, 1), de comprimento
    sqrt(2) ~ 1.414: o jogador andaria 41% mais depressa na diagonal.
    Dividindo pelo comprimento, todas as direcções têm comprimento 1.
    Teclas opostas anulam-se (esquerda + direita = 0).
    """
    dx = float(direita) - float(esquerda)
    dy = float(baixo) - float(cima)      # Y cresce para baixo
    comprimento = math.hypot(dx, dy)
    if comprimento == 0:
        return 0.0, 0.0
    return dx / comprimento, dy / comprimento


class Input:

    def __init__(self, window, teclas: dict = config.TECLAS):
        self.window = window
        self.teclas = teclas
        self._carregadas: set[int] = set()
        self.clique: tuple[float, float] | None = None   # clique deste frame (mundo)

    # -- chamado pelo Game ---------------------------------------------------
    def inicio_frame(self) -> None:
        self._carregadas.clear()
        self.clique = None

    def processar(self, evento) -> None:
        if evento.type == pygame.KEYDOWN:
            self._carregadas.add(evento.key)
        elif evento.type == pygame.MOUSEBUTTONDOWN and evento.button == 1:
            self.clique = janela_para_mundo(*evento.pos, self.window.viewport)

    # -- perguntas das cenas -------------------------------------------------
    def segurada(self, accao: str) -> bool:
        estado = pygame.key.get_pressed()
        return any(estado[k] for k in self.teclas[accao])

    def carregada(self, accao: str) -> bool:
        return any(k in self._carregadas for k in self.teclas[accao])

    def direccao(self) -> tuple[float, float]:
        return vector_direccao(self.segurada("esquerda"), self.segurada("direita"),
                               self.segurada("cima"), self.segurada("baixo"))

    def rato(self) -> tuple[float, float]:
        """Posição actual do rato no MUNDO (já descontadas as barras)."""
        return self.window.rato_no_mundo()
