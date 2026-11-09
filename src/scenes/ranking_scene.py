"""Tabela do ranking (Top 10), lida do SQLite sempre que a cena abre."""

from src import config
from src.core.scene_manager import Scene
from src.ui.menu import Botao, Menu

W, H = config.MUNDO_LARGURA, config.MUNDO_ALTURA
COLUNAS = [("#", 150, "direita"), ("NOME", 190, "esquerda"), ("PONTOS", 650, "direita"),
           ("ONDA", 790, "direita"), ("DATA", 860, "esquerda")]
COR_CABECALHO = (0.6, 0.6, 0.75, 1)
COR_LINHA = (0.92, 0.92, 1.0, 1)
COR_DESTAQUE = (1.0, 0.85, 0.3, 1)
MEDALHAS = [(1.0, 0.84, 0.2, 1), (0.8, 0.82, 0.88, 1), (0.85, 0.55, 0.3, 1)]


class RankingScene(Scene):

    def __init__(self, destaque_id: int | None = None, depois_do_jogo: bool = False):
        """destaque_id: resultado acabado de gravar, desenhado a amarelo."""
        super().__init__()
        self.destaque_id = destaque_id
        self.depois_do_jogo = depois_do_jogo

    def on_enter(self) -> None:
        self.resultados = self.game.ranking.top(config.TAMANHO_RANKING)
        itens = ([("Jogar de novo", "jogar"), ("Menu principal", "menu")]
                 if self.depois_do_jogo else [("Voltar", "voltar")])
        # Botões lado a lado, centrados na horizontal
        x0 = W / 2 - 200 * (len(itens) - 1)
        self.menu = Menu([Botao(t, a, x0 + 400 * i, 650, 340)
                          for i, (t, a) in enumerate(itens)])

    def update(self, dt: float) -> None:
        inp = self.game.input
        # No menu horizontal, esquerda/direita também navegam.
        if inp.carregada("esquerda"):
            self.menu.indice = (self.menu.indice - 1) % len(self.menu.botoes)
        if inp.carregada("direita"):
            self.menu.indice = (self.menu.indice + 1) % len(self.menu.botoes)
        accao = self.menu.update(inp)
        if inp.carregada("voltar"):
            accao = "menu" if self.depois_do_jogo else "voltar"
        if not accao:
            return
        self.game.audio.tocar("clique")
        if accao == "voltar":
            self.manager.pop()
        elif accao == "jogar":
            from src.scenes.play_scene import PlayScene
            self.manager.replace(PlayScene())
        elif accao == "menu":
            from src.scenes.menu_scene import MenuScene
            self.manager.replace(MenuScene())

    def render(self, r) -> None:
        txt = self.game.texto
        r.rect(W / 2, H / 2, W, H, (0.07, 0.07, 0.12, 1))
        txt.desenhar(r, "RANKING", W / 2, 60, 80, (0.45, 0.9, 1.0, 1), alinhar="centro")

        y = 130
        for titulo, x, alinhar in COLUNAS:
            txt.desenhar(r, titulo, x, y, 26, COR_CABECALHO, alinhar=alinhar)
        r.rect(W / 2, y + 20, 1000, 2, COR_CABECALHO)

        if not self.resultados:
            txt.desenhar(r, "Ainda não há resultados. Joga uma partida!", W / 2, 330, 36,
                         COR_LINHA, alinhar="centro")
        for i, res in enumerate(self.resultados):
            y = 175 + i * 42
            cor = COR_DESTAQUE if res.id == self.destaque_id else COR_LINHA
            if res.id == self.destaque_id:
                r.rect(W / 2, y, 1020, 38, (1.0, 0.85, 0.3, 0.15))
            if i < 3:
                r.circulo(115, y, 13, MEDALHAS[i])
            valores = [f"{i + 1}.", res.nome, str(res.pontos), str(res.onda), res.data[:16]]
            for (_, x, alinhar), valor in zip(COLUNAS, valores):
                txt.desenhar(r, valor, x, y, 32, cor, alinhar=alinhar)

        self.menu.render(r, txt)
