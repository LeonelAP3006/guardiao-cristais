"""Sistema de animação por frames (independente do OpenGL).

Conceitos:
  - Animation : uma sequência de índices de frames + quanto tempo dura cada um.
                Ex.: andar = frames [2, 3, 4, 5], 0.11 s cada.
  - Animator  : guarda várias animações com nome ("parado", "andar") e
                sabe qual está a tocar. A entidade só diz animator.tocar("andar").

O tempo é acumulado com dt, por isso a animação tem a mesma velocidade
a 30 ou a 144 FPS (como o movimento).

O resultado é apenas um ÍNDICE de frame. Quem desenha pede ao SpriteSheet
as coordenadas UV desse índice. Separar "que frame" de "como desenhar"
permite testar este módulo sem placa gráfica.
"""


class Animation:

    def __init__(self, frames: list[int], duracao_frame: float, loop: bool = True):
        if not frames:
            raise ValueError("Uma animação precisa de pelo menos 1 frame")
        self.frames = frames
        self.duracao_frame = duracao_frame
        self.loop = loop
        self.reiniciar()

    def reiniciar(self) -> None:
        self.tempo = 0.0
        self.posicao = 0          # posição dentro da lista `frames`
        self.terminou = False

    def update(self, dt: float) -> None:
        if self.terminou:
            return
        self.tempo += dt
        # while (e não if): se o dt for grande, pode ser preciso saltar
        # vários frames de uma vez para não ficar atrasado.
        while self.tempo >= self.duracao_frame:
            self.tempo -= self.duracao_frame
            self.posicao += 1
            if self.posicao >= len(self.frames):
                if self.loop:
                    self.posicao = 0
                else:
                    self.posicao = len(self.frames) - 1
                    self.terminou = True
                    break

    @property
    def frame(self) -> int:
        """Índice do frame no spritesheet."""
        return self.frames[self.posicao]


class Animator:

    def __init__(self, animacoes: dict[str, Animation], inicial: str):
        self.animacoes = animacoes
        self.actual = inicial

    def tocar(self, nome: str) -> None:
        """Muda de animação. Se já está a tocar, NÃO reinicia.

        Este detalhe é importante: o jogador chama tocar("andar") em todos
        os frames enquanto anda. Se reiniciasse sempre, ficava preso no
        1.º frame e a animação nunca avançava.
        """
        if nome != self.actual:
            self.actual = nome
            self.animacoes[nome].reiniciar()

    def update(self, dt: float) -> None:
        self.animacoes[self.actual].update(dt)

    @property
    def frame(self) -> int:
        return self.animacoes[self.actual].frame
