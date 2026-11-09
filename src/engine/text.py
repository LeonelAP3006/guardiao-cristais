"""Texto em OpenGL.

O OpenGL não sabe desenhar letras. A técnica usada:
  1. O Pygame "rasteriza" a frase com uma fonte TrueType para uma imagem
     (Surface) com fundo transparente e letras BRANCAS.
  2. Essa imagem vira uma textura OpenGL (é uma imagem digital como outra).
  3. Desenhamos um quad com essa textura; a cor final vem do "tint"
     do Renderer (branco x cor = cor), por isso uma só textura serve
     para qualquer cor e até para fazer o texto desvanecer (alfa).

Cache: criar uma textura é caro (envia píxeis para a placa gráfica).
Guardamos as últimas frases desenhadas; "PONTOS 1520" só é recriado
quando o número muda. A cache tem limite (LRU) e liberta da placa
gráfica as texturas mais antigas, para não acumular memória.
"""

from collections import OrderedDict

import pygame

from src.engine.texture import Texture

BRANCO = (1.0, 1.0, 1.0, 1.0)


class TextRenderer:

    def __init__(self, limite_cache: int = 256):
        self._fontes: dict[int, pygame.font.Font] = {}
        self._cache: OrderedDict[tuple, Texture] = OrderedDict()
        self.limite = limite_cache

    def _fonte(self, tamanho: int) -> pygame.font.Font:
        if tamanho not in self._fontes:
            # None = fonte incluída no próprio Pygame: não precisamos de
            # distribuir ficheiros .ttf nem de nos preocupar com licenças.
            self._fontes[tamanho] = pygame.font.Font(None, tamanho)
        return self._fontes[tamanho]

    def textura(self, texto: str, tamanho: int) -> Texture:
        chave = (texto, tamanho)
        if chave in self._cache:
            self._cache.move_to_end(chave)          # usado agora: mais recente
            return self._cache[chave]
        superficie = self._fonte(tamanho).render(texto, True, (255, 255, 255))
        tex = Texture(superficie, suave=True)
        self._cache[chave] = tex
        if len(self._cache) > self.limite:
            _, antiga = self._cache.popitem(last=False)   # a menos usada
            antiga.libertar()
        return tex

    def desenhar(self, r, texto: str, x: float, y: float, tamanho: int = 32,
                 cor=BRANCO, alinhar: str = "esquerda") -> None:
        """Desenha `texto` com o centro vertical em y.

        alinhar: "esquerda" (x = início), "centro" (x = meio), "direita" (x = fim).
        """
        if not texto:
            return
        tex = self.textura(texto, tamanho)
        if alinhar == "centro":
            cx = x
        elif alinhar == "direita":
            cx = x - tex.largura / 2
        else:
            cx = x + tex.largura / 2
        r.sprite(tex, cx, y, tex.largura, tex.altura, cor=cor)

    def libertar(self) -> None:
        for t in self._cache.values():
            t.libertar()
        self._cache.clear()
