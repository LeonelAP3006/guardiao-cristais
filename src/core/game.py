"""Game loop: o ciclo que corre ~60 vezes por segundo até o jogo fechar.

Cada volta do ciclo (um "frame") faz sempre, por esta ordem:
  1. medir o tempo desde o frame anterior (delta time, dt);
  2. processar eventos (teclado, rato, fechar, redimensionar);
  3. actualizar a lógica da cena do topo, usando dt;
  4. desenhar as cenas;
  5. apresentar o frame (trocar buffers).

O Game é o "dono" dos serviços partilhados. As cenas chegam-lhes por
self.game.window / .input / .assets / .texto / .scenes.
"""

import pygame

from src import config
from src.core.assets import Assets
from src.core.input import Input
from src.core.scene_manager import SceneManager
from src.engine.renderer import Renderer
from src.engine.text import TextRenderer
from src.engine.window import Window


class Game:

    def __init__(self, window: Window):
        self.window = window
        self.renderer = Renderer()
        self.input = Input(window)
        self.assets = Assets()
        self.texto = TextRenderer()
        self.scenes = SceneManager(self)
        self.relogio = pygame.time.Clock()
        self.a_correr = True

    def parar(self) -> None:
        self.a_correr = False

    def executar(self, cena_inicial) -> None:
        self.scenes.push(cena_inicial)
        while self.a_correr and self.scenes.topo:
            # tick() espera o necessário para não passar de FPS_ALVO e devolve
            # os milissegundos desde a última chamada. Convertemos para segundos.
            dt = self.relogio.tick(config.FPS_ALVO) / 1000.0
            # Tecto de segurança: ver config.DT_MAXIMO.
            dt = min(dt, config.DT_MAXIMO)

            self._processar_eventos()
            self.scenes.update(dt)

            self.window.limpar()
            self.scenes.render(self.renderer)
            self.window.apresentar()

            # Enquanto não temos texto em OpenGL, o FPS vai para a barra de título.
            pygame.display.set_caption(
                f"{config.TITULO}  |  {self.relogio.get_fps():.0f} FPS")
        self.assets.libertar()
        self.texto.libertar()

    def _processar_eventos(self) -> None:
        self.input.inicio_frame()
        for evento in pygame.event.get():
            # Eventos globais tratados pelo próprio loop:
            if evento.type == pygame.QUIT:
                self.parar()
            elif evento.type == pygame.VIDEORESIZE:
                self.window.on_resize(evento.w, evento.h)
            self.input.processar(evento)
            # A cena do topo também recebe o evento em bruto, se precisar.
            self.scenes.handle_event(evento)
