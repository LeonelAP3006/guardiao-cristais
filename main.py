"""Ponto de entrada do jogo.  Executar a partir da raiz do projecto:

    python main.py
"""

import os
import sys

import pygame

from src.core.game import Game
from src.engine.window import Window
from src.scenes.play_scene import PlayScene


def main() -> int:
    # Garante que os caminhos relativos (assets/...) funcionam mesmo que o
    # jogo seja lançado de outra pasta (ex.: duplo clique ou VS Code).
    os.chdir(os.path.dirname(os.path.abspath(__file__)))

    pygame.init()
    try:
        window = Window()          # 1.º a janela: cria o contexto OpenGL
        game = Game(window)        # 2.º os serviços (input, assets, cenas)
        game.executar(PlayScene()) # 3.º a cena inicial (no Bloco 4: MenuScene)
    finally:
        pygame.quit()
    return 0


if __name__ == "__main__":
    sys.exit(main())
