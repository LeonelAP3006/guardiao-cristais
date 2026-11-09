"""Game loop: o ciclo que corre ~60 vezes por segundo até o jogo fechar.

Cada volta do ciclo (um "frame") faz sempre, por esta ordem:
  1. medir o tempo desde o frame anterior (delta time, dt);
  2. processar eventos (teclado, rato, fechar, redimensionar);
  3. actualizar a lógica da cena, usando dt;
  4. desenhar a cena;
  5. apresentar o frame (trocar buffers).

Contrato de uma cena (qualquer objecto com estes 3 métodos):
    handle_event(evento) -> None
    update(dt: float)    -> None
    render(renderer)     -> None
No Bloco 2 isto passa a ser gerido por um SceneManager (menu, jogo, pausa...).
"""

import pygame

from src import config
from src.engine.renderer import Renderer
from src.engine.window import Window


class Game:

    def __init__(self, window: Window, cena):
        self.window = window
        self.renderer = Renderer()
        self.cena = cena
        self.relogio = pygame.time.Clock()
        self.a_correr = True

    def parar(self) -> None:
        self.a_correr = False

    def executar(self) -> None:
        while self.a_correr:
            # tick() espera o necessário para não passar de FPS_ALVO e devolve
            # os milissegundos desde a última chamada. Convertemos para segundos.
            dt = self.relogio.tick(config.FPS_ALVO) / 1000.0
            # Tecto de segurança: ver config.DT_MAXIMO.
            dt = min(dt, config.DT_MAXIMO)

            self._processar_eventos()
            self.cena.update(dt)

            self.window.limpar()
            self.cena.render(self.renderer)
            self.window.apresentar()

            # Enquanto não temos texto em OpenGL, o FPS vai para a barra de título.
            pygame.display.set_caption(
                f"{config.TITULO}  |  {self.relogio.get_fps():.0f} FPS")

    def _processar_eventos(self) -> None:
        for evento in pygame.event.get():
            # Eventos globais tratados pelo próprio loop:
            if evento.type == pygame.QUIT:
                self.parar()
            elif evento.type == pygame.VIDEORESIZE:
                self.window.on_resize(evento.w, evento.h)
            # Todos os eventos seguem também para a cena activa.
            self.cena.handle_event(evento)
