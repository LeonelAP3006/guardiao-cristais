"""Como jogar: regras e controlos, com os ícones reais do jogo."""

from src import config
from src.core.scene_manager import Scene
from src.systems.effects import FRAME

W, H = config.MUNDO_LARGURA, config.MUNDO_ALTURA
BRANCO = (0.92, 0.92, 1.0, 1.0)
CINZA = (0.7, 0.7, 0.8, 1.0)


class HelpScene(Scene):

    def on_enter(self) -> None:
        a = self.game.assets
        self.icones = {
            "explorador": (a.folha("explorador"), 0),
            "cristal": (a.folha("cristal"), 0),
            "sentinela": (a.folha("sentinela"), 2),
            "lamina": (a.folha("lamina"), 0),
            "escudo": (a.folha("powerups"), FRAME["escudo"]),
            "velocidade": (a.folha("powerups"), FRAME["velocidade"]),
            "vida": (a.folha("powerups"), FRAME["vida"]),
        }

    def update(self, dt: float) -> None:
        inp = self.game.input
        if inp.carregada("voltar") or inp.carregada("confirmar") or inp.clique:
            self.game.audio.tocar("clique")
            self.manager.pop()

    def render(self, r) -> None:
        txt = self.game.texto
        r.rect(W / 2, H / 2, W, H, (0.07, 0.07, 0.12, 1))
        txt.desenhar(r, "COMO JOGAR", W / 2, 70, 72, (0.45, 0.9, 1.0, 1), alinhar="centro")

        linhas = [
            ("explorador", "Move-te com as setas ou WASD. ESC pausa."),
            ("cristal", "Apanha cristais: 100 pontos x onda. A cada 8, nova onda (+500)."),
            ("sentinela", "Sentinelas patrulham e perseguem-te se te VIREM. Esconde-te!"),
            ("lamina", "Lâminas e lasers magoam. Cada toque tira 1 vida (tens 3)."),
            ("escudo", "Escudo: 5 s sem levar dano."),
            ("velocidade", "Velocidade: 5 s a 160% da velocidade."),
            ("vida", "Vida: +1 vida (máx. 5). Com vidas cheias vale 250 pontos."),
        ]
        for i, (icone, frase) in enumerate(linhas):
            y = 160 + i * 66
            folha, frame = self.icones[icone]
            r.sprite(folha.textura, 200, y, 56, 56, uv=folha.uv(frame))
            txt.desenhar(r, frase, 250, y, 32, BRANCO)

        txt.desenhar(r, "Sobreviver também dá 10 pontos por segundo.  F1: ver a IA e as hitboxes.",
                     W / 2, 640, 26, CINZA, alinhar="centro")
        txt.desenhar(r, "ESC / Enter / clique  -  voltar", W / 2, 685, 26, CINZA, alinhar="centro")
