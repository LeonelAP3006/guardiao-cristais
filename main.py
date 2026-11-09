"""Ponto de entrada do jogo.  Executar a partir da raiz do projecto:

    python main.py
"""

import os
import sys

import pygame

from src.core.game import Game
from src.engine.window import Window
from src.scenes.demo_scene import DemoScene


def main() -> int:
    # Garante que os caminhos relativos (assets/...) funcionam mesmo que o
    # jogo seja lançado de outra pasta (ex.: duplo clique ou VS Code).
    os.chdir(os.path.dirname(os.path.abspath(__file__)))

    pygame.init()
    try:
        window = Window()                 # 1.º a janela: cria o contexto OpenGL
        cena = DemoScene()                # 2.º recursos (texturas exigem contexto)
        game = Game(window, cena)
        cena.game = game                  # a cena precisa do jogo para sair/viewport
        game.executar()
    finally:
        pygame.quit()
    return 0


if __name__ == "__main__":
    sys.exit(main())
