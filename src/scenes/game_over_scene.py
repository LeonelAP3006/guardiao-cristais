"""Game Over: mostra o resultado e pede o nome para o ranking.

Fluxo:  escrever nome -> Enter -> grava no SQLite -> RankingScene (destaque)
        ESC -> não grava -> menu principal

O campo de texto usa os eventos TEXTINPUT (via Input.texto), que já
trazem acentos e maiúsculas resolvidos pelo sistema operativo. Por isso
o campo NÃO usa as acções com letras (pausa = P, sair = Q): escrever
"Pedro" não pode pausar nem fechar o jogo.
"""

from src import config
from src.core.scene_manager import Scene
from src.data.ranking import limpar_nome

W, H = config.MUNDO_LARGURA, config.MUNDO_ALTURA
ESPERA = 0.6     # s antes de aceitar teclas (quem morre a carregar não salta o ecrã)


class GameOverScene(Scene):

    def __init__(self, sessao):
        super().__init__()
        self.sessao = sessao
        self.tempo = 0.0

    def on_enter(self) -> None:
        self.nome = self.game.ultimo_nome
        self.lugar = self.game.ranking.posicao_para(self.sessao.pontos)
        self.game.audio.musica(False)
        self.game.audio.tocar("gameover")

    def update(self, dt: float) -> None:
        self.tempo += dt
        if self.tempo < ESPERA:
            return
        inp = self.game.input
        if inp.texto:
            self.nome = (self.nome + inp.texto)[:config.NOME_MAXIMO]
        if inp.carregada("apagar"):
            self.nome = self.nome[:-1]

        if inp.carregada("enter") or inp.clique:
            self._guardar()
        elif inp.carregada("voltar"):
            from src.scenes.menu_scene import MenuScene
            self.manager.replace(MenuScene())

    def _guardar(self) -> None:
        s = self.sessao
        nome = limpar_nome(self.nome)
        self.game.ultimo_nome = nome
        novo_id = self.game.ranking.registar(nome, s.pontos, s.onda,
                                             s.cristais_total, s.tempo_total)
        self.game.audio.tocar("clique")
        from src.scenes.ranking_scene import RankingScene
        self.manager.replace(RankingScene(destaque_id=novo_id, depois_do_jogo=True))

    def render(self, r) -> None:
        t, s = self.game.texto, self.sessao
        r.rect(W / 2, H / 2, W, H, (0.08, 0.04, 0.08, 1))
        t.desenhar(r, "GAME OVER", W / 2, 130, 120, (1, 0.3, 0.35, 1), alinhar="centro")
        t.desenhar(r, f"Pontuação: {s.pontos}", W / 2, 250, 56, (1, 0.85, 0.3, 1),
                   alinhar="centro")
        minutos, segundos = divmod(int(s.tempo_total), 60)
        t.desenhar(r, f"Onda {s.onda}   -   {s.cristais_total} cristais   -   "
                      f"{minutos}:{segundos:02d} sobrevividos",
                   W / 2, 315, 34, alinhar="centro")
        lugar = (f"Entras em {self.lugar}.º lugar no ranking!"
                 if self.lugar <= config.TAMANHO_RANKING else "Fora do Top 10 desta vez.")
        t.desenhar(r, lugar, W / 2, 375, 34, (0.5, 0.9, 1, 1), alinhar="centro")

        # Campo de texto com cursor a piscar
        t.desenhar(r, "O teu nome:", W / 2, 450, 32, (0.8, 0.8, 0.9, 1), alinhar="centro")
        r.rect(W / 2, 505, 460, 64, (0.6, 0.5, 0.7, 1))
        r.rect(W / 2, 505, 452, 56, (0.12, 0.1, 0.18, 1))
        cursor = "_" if int(self.tempo * 2.5) % 2 == 0 else " "
        t.desenhar(r, self.nome + cursor, W / 2, 507, 44, alinhar="centro")

        if self.tempo >= ESPERA:
            t.desenhar(r, "Enter  -  guardar no ranking        ESC  -  não guardar",
                       W / 2, 610, 28, (0.75, 0.75, 0.85, 1), alinhar="centro")
