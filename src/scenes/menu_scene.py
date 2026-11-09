"""Menu principal: primeira cena do jogo.

O fundo é animado com os próprios elementos do jogo (lâminas a rodar,
cristal a flutuar), o que mostra transformações logo no primeiro ecrã.
A opção "Som" funciona como ecrã de configurações simples.
"""

import math

from src import config
from src.core.scene_manager import Scene
from src.entities.arena import Arena
from src.ui.menu import Menu

W, H = config.MUNDO_LARGURA, config.MUNDO_ALTURA


class MenuScene(Scene):

    def on_enter(self) -> None:
        a = self.game.assets
        self.arena = Arena(a.textura("parede", repetir=True))
        self.arena.paredes = self.arena.paredes[:4]           # só o contorno
        self.lamina = a.folha("lamina")
        self.cristal = a.folha("cristal")
        self.tempo = 0.0
        self._criar_menu()
        self.game.audio.musica(True)

    def _criar_menu(self) -> None:
        indice = self.menu.indice if hasattr(self, "menu") else 0
        som = "Som: ligado" if self.game.audio.ligado else "Som: desligado"
        self.menu = Menu.vertical([("Jogar", "jogar"), ("Como jogar", "ajuda"),
                                   ("Ranking", "ranking"), (som, "som"), ("Sair", "sair")],
                                  W / 2, 310, espaco=72)
        self.menu.indice = indice

    def update(self, dt: float) -> None:
        self.tempo += dt
        inp = self.game.input
        if inp.carregada("voltar"):
            self.game.parar()
            return
        accao = self.menu.update(inp)
        if not accao:
            return
        self.game.audio.tocar("clique")
        if accao == "jogar":
            from src.scenes.play_scene import PlayScene
            self.manager.replace(PlayScene())
        elif accao == "ajuda":
            from src.scenes.help_scene import HelpScene
            self.manager.push(HelpScene())
        elif accao == "ranking":
            from src.scenes.ranking_scene import RankingScene
            self.manager.push(RankingScene())
        elif accao == "som":
            self.game.audio.alternar()
            self._criar_menu()
        elif accao == "sair":
            self.game.parar()

    def render(self, r) -> None:
        t, txt = self.tempo, self.game.texto
        self.arena.render(r)
        # Decoração animada: rotação (lâminas) e translação em seno (cristais)
        for x, sentido in ((200, 1), (W - 200, -1)):
            r.sprite(self.lamina.textura, x, 470, 140, 140, angulo=sentido * t * 120)
            r.sprite(self.cristal.textura, x, 240 + 10 * math.sin(t * 3 + x), 80, 80,
                     uv=self.cristal.uv(int(t * 8)))

        # Título com sombra (o mesmo texto desenhado 2 vezes, deslocado)
        escala = 1 + 0.03 * math.sin(t * 2)
        txt.desenhar(r, "GUARDIÃO DOS CRISTAIS", W / 2 + 4, 154, int(92 * escala),
                     (0.1, 0.05, 0.2, 1), alinhar="centro")
        txt.desenhar(r, "GUARDIÃO DOS CRISTAIS", W / 2, 150, int(92 * escala),
                     (0.45, 0.9, 1.0, 1), alinhar="centro")
        txt.desenhar(r, "Recolhe cristais. Foge das sentinelas.", W / 2, 230, 32,
                     (0.8, 0.8, 0.9, 1), alinhar="centro")
        self.menu.render(r, txt)
        txt.desenhar(r, "Setas/WASD + Enter  ou  rato", W / 2, H - 52, 24,
                     (0.6, 0.6, 0.7, 1), alinhar="centro")
