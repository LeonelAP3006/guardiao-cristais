"""Gestor de áudio: música de fundo e efeitos sonoros.

Porque é que o som NÃO bloqueia o game loop?
  Sound.play() não espera que o som acabe: entrega-o ao misturador
  (mixer) do SDL, que corre na sua PRÓPRIA thread e mistura até 8 canais
  ao mesmo tempo. A chamada volta imediatamente e o frame continua.
  A música usa pygame.mixer.music, que lê o ficheiro aos bocados
  (streaming) em vez de o carregar todo para a memória.

Robustez: se o PC não tiver placa de som (ou estiver sem colunas),
mixer.init() falha. Em vez de o jogo rebentar, o Audio fica "mudo":
todos os métodos passam a não fazer nada. O resto do código não precisa
de saber; chama tocar("cristal") e pronto.

Comunicação por EVENTOS: as cenas dizem o que ACONTECEU ("cristal",
"dano"), não que ficheiro tocar. Trocar um som é só trocar o .wav.
"""

import os

import pygame

from src import config

EFEITOS = ["cristal", "dano", "powerup", "onda", "gameover", "clique"]


class Audio:

    def __init__(self, pasta: str = os.path.join(config.PASTA_ASSETS, "sounds")):
        self.pasta = pasta
        self.sons: dict[str, pygame.mixer.Sound] = {}
        self.ligado = True
        self.disponivel = False
        try:
            if not pygame.mixer.get_init():
                pygame.mixer.init()
            for nome in EFEITOS:
                caminho = os.path.join(pasta, f"{nome}.wav")
                if os.path.exists(caminho):
                    som = pygame.mixer.Sound(caminho)
                    som.set_volume(config.VOLUME_EFEITOS)
                    self.sons[nome] = som
            self.disponivel = True
        except pygame.error as erro:
            print(f"[áudio] desactivado: {erro}")

    def tocar(self, evento: str) -> None:
        if self.disponivel and self.ligado and evento in self.sons:
            self.sons[evento].play()

    def musica(self, tocar: bool = True) -> None:
        if not self.disponivel:
            return
        if tocar and self.ligado:
            if not pygame.mixer.music.get_busy():
                caminho = os.path.join(self.pasta, "musica.wav")
                if os.path.exists(caminho):
                    pygame.mixer.music.load(caminho)
                    pygame.mixer.music.set_volume(config.VOLUME_MUSICA)
                    pygame.mixer.music.play(loops=-1)       # -1 = repetir sempre
        else:
            pygame.mixer.music.stop()

    def alternar(self) -> bool:
        """Liga/desliga todo o som (opção do menu). Devolve o novo estado."""
        self.ligado = not self.ligado
        if self.disponivel:
            if self.ligado:
                self.musica(True)
            else:
                pygame.mixer.stop()
                pygame.mixer.music.stop()
        return self.ligado
