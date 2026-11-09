"""Pausa: cena transparente empilhada por cima do jogo.

Como só a cena do topo é actualizada, o jogo por baixo fica congelado,
mas continua a ser desenhado (transparente = True), escurecido por um véu.
"""

from src import config
from src.core.scene_manager import Scene
from src.ui.menu import Menu

W, H = config.MUNDO_LARGURA, config.MUNDO_ALTURA


class PauseScene(Scene):
    transparente = True

    def on_enter(self) -> None:
        self.menu = Menu.vertical([("Retomar", "retomar"), ("Reiniciar", "reiniciar"),
                                   ("Menu principal", "menu"), ("Sair do jogo", "sair")],
                                  W / 2, 300)

    def update(self, dt: float) -> None:
        inp = self.game.input
        if inp.carregada("pausa"):
            self.manager.pop()
            return
        accao = self.menu.update(inp)
        if accao:
            self.game.audio.tocar("clique")
        if accao == "retomar":
            self.manager.pop()
        elif accao == "reiniciar":
            from src.scenes.play_scene import PlayScene
            self.manager.replace(PlayScene())
        elif accao == "menu":
            from src.scenes.menu_scene import MenuScene
            self.manager.replace(MenuScene())
        elif accao == "sair":
            self.game.parar()

    def render(self, r) -> None:
        r.rect(W / 2, H / 2, W, H, config.COR_PAUSA_VEU)
        self.game.texto.desenhar(r, "PAUSA", W / 2, 180, 96, alinhar="centro")
        self.menu.render(r, self.game.texto)
