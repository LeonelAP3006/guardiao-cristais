"""Game Over: mostra o resultado da partida.

Cena OPACA que substitui o jogo (replace): a partida acabou, não há para
onde "voltar". No Bloco 4 esta cena pede o nome do jogador e grava a
pontuação no ranking (SQLite) antes de mostrar a tabela.
"""

from src import config
from src.core.scene_manager import Scene

W, H = config.MUNDO_LARGURA, config.MUNDO_ALTURA


class GameOverScene(Scene):

    def __init__(self, sessao):
        super().__init__()
        self.sessao = sessao
        self.tempo = 0.0

    def update(self, dt: float) -> None:
        self.tempo += dt
        inp = self.game.input
        # Meio segundo de espera: quem estava a carregar em teclas ao morrer
        # não salta o ecrã de Game Over sem querer.
        if self.tempo < 0.5:
            return
        if inp.carregada("confirmar") or inp.clique:
            from src.scenes.play_scene import PlayScene
            self.manager.replace(PlayScene())
        elif inp.carregada("sair") or inp.carregada("pausa"):
            self.game.parar()

    def render(self, r) -> None:
        t, s = self.game.texto, self.sessao
        r.rect(W / 2, H / 2, W, H, (0.08, 0.04, 0.08, 1))
        t.desenhar(r, "GAME OVER", W / 2, 200, 120, (1, 0.3, 0.35, 1), alinhar="centro")
        t.desenhar(r, f"Pontuação: {s.pontos}", W / 2, 330, 56,
                   (1, 0.85, 0.3, 1), alinhar="centro")
        minutos, segundos = divmod(int(s.tempo_total), 60)
        t.desenhar(r, f"Onda {s.onda}   -   {s.cristais_total} cristais   -   "
                      f"{minutos}:{segundos:02d} sobrevividos",
                   W / 2, 400, 34, alinhar="centro")
        if self.tempo >= 0.5:
            t.desenhar(r, "Enter / clique  -  jogar de novo        Q / ESC  -  sair",
                       W / 2, 560, 30, (0.75, 0.75, 0.85, 1), alinhar="centro")
