"""Ponto de entrada do jogo.  Executar a partir da raiz do projecto:

    python main.py
"""

import os
import sys

import pygame

from src.core.game import Game
from src.engine.window import Window
from src.scenes.menu_scene import MenuScene


def main() -> int:
    # Garante que os caminhos relativos (assets/, dados/) funcionam mesmo que o
    # jogo seja lançado de outra pasta (ex.: duplo clique ou VS Code).
    os.chdir(os.path.dirname(os.path.abspath(__file__)))

    # Buffer de áudio pequeno (512 amostras ~ 12 ms): os efeitos soam no
    # instante do evento. Tem de ser configurado ANTES de pygame.init().
    pygame.mixer.pre_init(44100, -16, 1, 512)
    pygame.init()
    try:
        window = Window()          # 1.º a janela: cria o contexto OpenGL
        game = Game(window)        # 2.º os serviços (input, assets, áudio, ranking, cenas)
        game.executar(MenuScene()) # 3.º a cena inicial
    finally:
        pygame.quit()
    return 0


if __name__ == "__main__":
    sys.exit(main())
