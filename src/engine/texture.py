"""Imagens digitais -> texturas OpenGL, e spritesheets.

Fluxo de uma imagem até ao ecrã:
  ficheiro PNG --(Pygame)--> Surface (matriz de píxeis RGBA na RAM)
               --(tobytes)--> sequência de bytes R,G,B,A,R,G,B,A,...
               --(glTexImage2D)--> textura na memória da placa gráfica
  Depois, ao desenhar um quad, dizemos que ponto da textura (u, v)
  corresponde a cada vértice: isto é o "mapeamento de textura".
"""

import pygame
from OpenGL.GL import (
    GL_CLAMP_TO_EDGE, GL_LINEAR, GL_NEAREST, GL_REPEAT, GL_RGBA, GL_TEXTURE_2D,
    GL_TEXTURE_MAG_FILTER, GL_TEXTURE_MIN_FILTER, GL_TEXTURE_WRAP_S,
    GL_TEXTURE_WRAP_T, GL_UNPACK_ALIGNMENT, GL_UNSIGNED_BYTE,
    glBindTexture, glDeleteTextures, glGenTextures, glPixelStorei,
    glTexImage2D, glTexParameteri,
)


def _superficie_para_bytes(surface: pygame.Surface) -> bytes:
    # pygame >= 2.1.3 tem tobytes; versões antigas só têm tostring.
    conversor = getattr(pygame.image, "tobytes", None) or pygame.image.tostring
    # flipped=False: a primeira linha dos bytes é a linha de CIMA da imagem.
    # Como a nossa projecção tem o Y a crescer para baixo, v=0 fica em cima
    # e não é preciso inverter a imagem.
    return conversor(surface, "RGBA", False)


class Texture:
    """Uma imagem carregada na placa gráfica, identificada por um id OpenGL."""

    def __init__(self, surface: pygame.Surface, repetir: bool = False,
                 suave: bool = False):
        self.largura, self.altura = surface.get_size()
        self.repetir = repetir
        dados = _superficie_para_bytes(surface)

        self.id = glGenTextures(1)
        glBindTexture(GL_TEXTURE_2D, self.id)

        # Filtro usado quando a textura é desenhada maior/menor que o original:
        #  - GL_NEAREST: cada píxel vira um bloco nítido (ideal para pixel art).
        #  - GL_LINEAR : mistura píxeis vizinhos, suave (melhor para texto).
        filtro = GL_LINEAR if suave else GL_NEAREST
        glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MIN_FILTER, filtro)
        glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MAG_FILTER, filtro)
        # Modo de "embrulho" quando u ou v saem de 0..1:
        #  - CLAMP_TO_EDGE (sprites): evita puxar píxeis da borda oposta.
        #  - REPEAT (paredes, chão): u=0..4 desenha a imagem 4 vezes seguidas,
        #    ou seja, um padrão em mosaico com uma só textura pequena.
        modo = GL_REPEAT if repetir else GL_CLAMP_TO_EDGE
        glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_WRAP_S, modo)
        glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_WRAP_T, modo)

        glPixelStorei(GL_UNPACK_ALIGNMENT, 1)
        glTexImage2D(GL_TEXTURE_2D, 0, GL_RGBA, self.largura, self.altura, 0,
                     GL_RGBA, GL_UNSIGNED_BYTE, dados)
        glBindTexture(GL_TEXTURE_2D, 0)

    @classmethod
    def carregar(cls, caminho: str, repetir: bool = False) -> "Texture":
        # Não usamos convert_alpha(): com uma janela OPENGL não existe
        # superfície de ecrã do Pygame para onde converter.
        return cls(pygame.image.load(caminho), repetir=repetir)

    def libertar(self) -> None:
        glDeleteTextures([self.id])


class SpriteSheet:
    """Uma textura dividida numa grelha de frames do mesmo tamanho.

    Em vez de carregar 1 ficheiro por frame, carregamos uma só imagem com
    todos os frames lado a lado e escolhemos o frame pelas coordenadas UV.
    Menos ficheiros, menos trocas de textura, e é assim que os jogos 2D fazem.
    """

    def __init__(self, textura: Texture, frame_w: int, frame_h: int):
        self.textura = textura
        self.frame_w = frame_w
        self.frame_h = frame_h
        self.colunas = textura.largura // frame_w
        self.linhas = textura.altura // frame_h

    @property
    def total_frames(self) -> int:
        return self.colunas * self.linhas

    def uv(self, indice: int) -> tuple[float, float, float, float]:
        """Rectângulo (u0, v0, u1, v1) do frame `indice`, em 0..1.

        As coordenadas UV são normalizadas: u=0 é a borda esquerda da imagem
        e u=1 a direita, seja qual for o tamanho em píxeis.
        """
        indice %= self.total_frames
        col = indice % self.colunas
        lin = indice // self.colunas
        u0 = col * self.frame_w / self.textura.largura
        v0 = lin * self.frame_h / self.textura.altura
        u1 = u0 + self.frame_w / self.textura.largura
        v1 = v0 + self.frame_h / self.textura.altura
        return u0, v0, u1, v1
