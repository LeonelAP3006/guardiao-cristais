"""Cenas (ecrãs do jogo) e o gestor que as troca.

Porquê uma PILHA de cenas e não só "a cena actual"?
  Ao pausar, queremos ver o jogo congelado POR BAIXO do menu de pausa.
  Com uma pilha:   [PlayScene, PauseScene]
    - só a cena do TOPO recebe eventos e é actualizada (o jogo fica parado);
    - TODAS são desenhadas, de baixo para cima (o jogo aparece por trás).
  Retomar = pop() -> volta a [PlayScene] exactamente no mesmo estado.

Operações:
  push(cena)    : põe uma cena por cima (ex.: pausa)
  pop()         : tira a cena do topo (ex.: retomar)
  replace(cena) : esvazia a pilha e começa noutra (ex.: menu -> jogo)
"""


class Scene:
    """Classe base. Cada ecrã do jogo herda desta e reescreve o que precisar."""

    #: Se True, a cena de baixo continua a ser desenhada (overlay/transparente).
    transparente = False

    def __init__(self):
        self.manager: "SceneManager | None" = None

    @property
    def game(self):
        return self.manager.game

    # Ciclo de vida
    def on_enter(self) -> None:
        """Chamado quando a cena fica no topo pela 1.ª vez."""

    def on_exit(self) -> None:
        """Chamado quando a cena sai da pilha."""

    # Ciclo do jogo
    def handle_event(self, evento) -> None:
        pass

    def update(self, dt: float) -> None:
        pass

    def render(self, renderer) -> None:
        pass


class SceneManager:

    def __init__(self, game=None):
        self.game = game
        self.pilha: list[Scene] = []

    @property
    def topo(self) -> Scene | None:
        return self.pilha[-1] if self.pilha else None

    # -- operações -----------------------------------------------------------
    def push(self, cena: Scene) -> None:
        cena.manager = self
        self.pilha.append(cena)
        cena.on_enter()

    def pop(self) -> Scene | None:
        if not self.pilha:
            return None
        cena = self.pilha.pop()
        cena.on_exit()
        return cena

    def replace(self, cena: Scene) -> None:
        while self.pilha:
            self.pop()
        self.push(cena)

    # -- delegação do game loop ----------------------------------------------
    def handle_event(self, evento) -> None:
        if self.topo:
            self.topo.handle_event(evento)

    def update(self, dt: float) -> None:
        if self.topo:
            self.topo.update(dt)

    def render(self, renderer) -> None:
        # Desenha a partir da cena opaca mais alta: não vale a pena desenhar
        # cenas que ficam completamente tapadas por outra opaca.
        inicio = len(self.pilha) - 1
        while inicio > 0 and self.pilha[inicio].transparente:
            inicio -= 1
        for cena in self.pilha[max(inicio, 0):]:
            cena.render(renderer)
