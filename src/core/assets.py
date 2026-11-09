"""Asset Manager: carrega cada ficheiro UMA vez e reutiliza.

Sem isto, se 10 inimigos fizessem Texture.carregar("inimigo.png"), teríamos
10 cópias iguais na placa gráfica e 10 leituras do disco. Com a cache,
o 1.º pedido carrega e os seguintes recebem o mesmo objecto.

Importante: só pode ser usado DEPOIS de a janela existir, porque criar
texturas exige um contexto OpenGL activo.
"""

import os

from src import config
from src.engine.texture import SpriteSheet, Texture


class Assets:

    def __init__(self, pasta: str = config.PASTA_ASSETS):
        self.pasta = pasta
        self._texturas: dict[tuple, Texture] = {}

    def _caminho(self, *partes: str) -> str:
        return os.path.join(self.pasta, *partes)

    def textura(self, nome: str, repetir: bool = False) -> Texture:
        """Textura de assets/sprites/<nome>.png (em cache)."""
        chave = (nome, repetir)
        if chave not in self._texturas:
            caminho = self._caminho("sprites", f"{nome}.png")
            self._texturas[chave] = Texture.carregar(caminho, repetir=repetir)
        return self._texturas[chave]

    def folha(self, nome: str, frame_w: int = config.TAMANHO_FRAME,
              frame_h: int = config.TAMANHO_FRAME) -> SpriteSheet:
        return SpriteSheet(self.textura(nome), frame_w, frame_h)

    def libertar(self) -> None:
        for t in self._texturas.values():
            t.libertar()
        self._texturas.clear()
