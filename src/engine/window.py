"""Janela, contexto OpenGL e janela-visor sem distorção (letterbox).

Responsabilidade deste módulo:
  1. Criar a janela com um contexto OpenGL (via Pygame).
  2. Configurar a projecção ortográfica do mundo 2D.
  3. Recalcular o viewport sempre que a janela é redimensionada,
     mantendo a proporção 16:9 do mundo (requisito "janela-visor sem distorção").
  4. Converter coordenadas do rato (janela) para coordenadas do mundo.

A matemática do viewport está em funções PURAS (sem OpenGL), para poder
ser testada com pytest sem abrir janela nenhuma (ver tests/test_viewport.py).
"""

from dataclasses import dataclass

import pygame
from OpenGL.GL import (
    GL_BLEND, GL_COLOR_BUFFER_BIT, GL_MODELVIEW, GL_ONE_MINUS_SRC_ALPHA,
    GL_PROJECTION, GL_SCISSOR_TEST, GL_SRC_ALPHA,
    glBlendFunc, glClear, glClearColor, glDisable, glEnable,
    glLoadIdentity, glMatrixMode, glOrtho, glScissor, glViewport,
)

from src import config


# ---------------------------------------------------------------------------
# Matemática pura (testável sem OpenGL)
# ---------------------------------------------------------------------------
@dataclass(frozen=True)
class Viewport:
    """Rectângulo da janela onde o mundo é desenhado.

    x, y_topo : canto superior esquerdo, em píxeis da janela (y para baixo,
                como o Pygame e o rato).
    largura, altura : tamanho em píxeis.
    escala : quantos píxeis do ecrã correspondem a 1 unidade do mundo.
    """
    x: int
    y_topo: int
    largura: int
    altura: int
    escala: float


def calcular_viewport(janela_w: int, janela_h: int,
                      mundo_w: int, mundo_h: int) -> Viewport:
    """Maior rectângulo com a proporção do mundo que cabe na janela, centrado.

    Exemplo com mundo 1280x720 (16:9):
      - janela 1920x1080 -> escala 1.5, sem barras;
      - janela 800x800   -> escala 0.625, viewport 800x450, barras em cima/baixo;
      - janela 1600x600  -> escala 0.833, viewport 1067x600, barras laterais.

    A escala é o MÍNIMO das duas razões: se usássemos uma escala diferente
    em x e em y, o círculo virava elipse (distorção). Com a mesma escala nos
    dois eixos, a forma é preservada; o espaço que sobra fica com barras.
    """
    escala = min(janela_w / mundo_w, janela_h / mundo_h)
    largura = round(mundo_w * escala)
    altura = round(mundo_h * escala)
    x = (janela_w - largura) // 2
    y_topo = (janela_h - altura) // 2
    return Viewport(x, y_topo, largura, altura, escala)


def janela_para_mundo(px: float, py: float, vp: Viewport) -> tuple[float, float]:
    """Converte uma posição do rato (píxeis da janela) para unidades do mundo.

    Primeiro descontamos o deslocamento das barras (vp.x, vp.y_topo);
    depois dividimos pela escala. Sem isto, um clique num botão do menu
    seria detectado no sítio errado sempre que a janela tivesse barras.
    """
    return (px - vp.x) / vp.escala, (py - vp.y_topo) / vp.escala


# ---------------------------------------------------------------------------
# Janela OpenGL
# ---------------------------------------------------------------------------
class Window:
    """Dona da janela e do contexto OpenGL. Só existe UMA na aplicação."""

    def __init__(self, largura: int = config.JANELA_LARGURA,
                 altura: int = config.JANELA_ALTURA,
                 titulo: str = config.TITULO):
        # OPENGL   -> a superfície da janela é um contexto OpenGL
        #             (a partir daqui NÃO se usa screen.blit do Pygame).
        # DOUBLEBUF-> desenhamos num buffer escondido e trocamos no fim (flip),
        #             evitando que o jogador veja o frame a meio de ser desenhado.
        # RESIZABLE-> o utilizador pode redimensionar; tratamos isso em on_resize.
        flags = pygame.OPENGL | pygame.DOUBLEBUF | pygame.RESIZABLE
        pygame.display.set_mode((largura, altura), flags)
        pygame.display.set_caption(titulo)

        self.largura = largura
        self.altura = altura
        self.viewport = calcular_viewport(largura, altura,
                                          config.MUNDO_LARGURA, config.MUNDO_ALTURA)
        self._configurar_opengl()

    # -- configuração inicial ------------------------------------------------
    def _configurar_opengl(self) -> None:
        # Transparência: permite que os píxeis transparentes dos PNG
        # (canal alfa) não apareçam como quadrados pretos.
        glEnable(GL_BLEND)
        glBlendFunc(GL_SRC_ALPHA, GL_ONE_MINUS_SRC_ALPHA)

        # Projecção ortográfica: mapeia o mundo 1280x720 para o viewport.
        # glOrtho(esquerda, direita, baixo, cima, perto, longe)
        # Passamos baixo=720 e cima=0, por isso o eixo Y cresce PARA BAIXO,
        # tal como no Pygame, nas imagens PNG e nas coordenadas do rato.
        # Isto evita inversões constantes entre sistemas de coordenadas.
        glMatrixMode(GL_PROJECTION)
        glLoadIdentity()
        glOrtho(0, config.MUNDO_LARGURA, config.MUNDO_ALTURA, 0, -1, 1)

        # A matriz MODELVIEW guarda as transformações dos objectos
        # (translação, rotação, escala). Começa como identidade.
        glMatrixMode(GL_MODELVIEW)
        glLoadIdentity()

        self._aplicar_viewport()

    def _aplicar_viewport(self) -> None:
        vp = self.viewport
        # glViewport mede o y a partir do FUNDO da janela (convenção OpenGL),
        # enquanto o nosso Viewport guarda o y a partir do TOPO.
        y_gl = self.altura - vp.y_topo - vp.altura
        glViewport(vp.x, y_gl, vp.largura, vp.altura)
        self._y_gl = y_gl

    # -- eventos -------------------------------------------------------------
    def on_resize(self, nova_largura: int, nova_altura: int) -> None:
        """Chamado pelo game loop quando chega um evento VIDEORESIZE.

        Nota: no Pygame 2 o contexto OpenGL sobrevive ao redimensionamento,
        por isso NÃO voltamos a chamar set_mode (isso poderia destruir o
        contexto e perder as texturas já carregadas). Basta recalcular o viewport.
        A projecção ortográfica não muda: o mundo continua a ser 1280x720.
        """
        self.largura = max(1, nova_largura)
        self.altura = max(1, nova_altura)
        self.viewport = calcular_viewport(self.largura, self.altura,
                                          config.MUNDO_LARGURA, config.MUNDO_ALTURA)
        self._aplicar_viewport()

    # -- desenho -------------------------------------------------------------
    def limpar(self) -> None:
        """Limpa a janela inteira a preto e a área de jogo com a cor da arena.

        glClear ignora o viewport e limpa a janela toda; por isso usamos o
        teste de tesoura (scissor) para limitar a segunda limpeza à área de jogo.
        O resultado são as barras pretas do letterbox à volta da arena.
        """
        glClearColor(*config.COR_BARRAS)
        glClear(GL_COLOR_BUFFER_BIT)

        vp = self.viewport
        glEnable(GL_SCISSOR_TEST)
        glScissor(vp.x, self._y_gl, vp.largura, vp.altura)
        glClearColor(*config.COR_FUNDO_ARENA)
        glClear(GL_COLOR_BUFFER_BIT)
        glDisable(GL_SCISSOR_TEST)

    @staticmethod
    def apresentar() -> None:
        """Troca o buffer de trás (já desenhado) com o da frente (visível)."""
        pygame.display.flip()

    def rato_no_mundo(self) -> tuple[float, float]:
        """Posição actual do rato em coordenadas do mundo."""
        mx, my = pygame.mouse.get_pos()
        return janela_para_mundo(mx, my, self.viewport)
