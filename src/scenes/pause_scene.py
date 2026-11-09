"""Pausa: cena transparente empilhada por cima do jogo.

Como só a cena do topo é actualizada, o jogo por baixo fica congelado,
mas continua a ser desenhado (transparente = True), escurecido por um véu.

Controlos: ESC/P/Enter/Espaço ou clique = retomar, Q = sair.
No Bloco 4 isto ganha botões (Retomar, Reiniciar, Menu).
"""

from src import config
from src.core.scene_manager import Scene

W, H = config.MUNDO_LARGURA, config.MUNDO_ALTURA


class PauseScene(Scene):
    transparente = True

    def update(self, dt: float) -> None:
        inp = self.game.input
        if inp.carregada("pausa") or inp.carregada("confirmar") or inp.clique:
            self.manager.pop()
        elif inp.carregada("sair"):
            self.game.parar()

    def render(self, r) -> None:
        t = self.game.texto
        r.rect(W / 2, H / 2, W, H, config.COR_PAUSA_VEU)
        t.desenhar(r, "PAUSA", W / 2, H / 2 - 40, 96, alinhar="centro")
        t.desenhar(r, "ESC / Enter / clique  -  retomar        Q  -  sair",
                   W / 2, H / 2 + 40, 30, (0.8, 0.8, 0.9, 1), alinhar="centro")
