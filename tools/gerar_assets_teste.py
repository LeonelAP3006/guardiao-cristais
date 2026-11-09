"""Gera assets PROVISÓRIOS (criados por nós, sem direitos de terceiros).

  assets/sprites/explorador.png : spritesheet 6 frames de 32x32
        frames 0-1 parado (respira), frames 2-5 a andar
  assets/sounds/teste.wav       : bip de 0,3 s para validar o áudio

Executar uma vez:  python tools/gerar_assets_teste.py
Mais tarde substituímos por arte CC0 (ex.: Kenney.nl) com o mesmo formato.
"""

import math
import os
import struct
import wave

os.environ.setdefault("SDL_VIDEODRIVER", "dummy")   # não abre janela
import pygame  # noqa: E402

RAIZ = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
F = 32  # tamanho de cada frame

PELE = (240, 200, 160)
CHAPEU = (150, 95, 45)
CAMISA = (60, 140, 200)
CALCAS = (60, 60, 90)
BOTAS = (50, 35, 25)
OLHO = (20, 20, 30)


def desenhar_frame(s: pygame.Surface, ox: int, perna: int, respira: int) -> None:
    """Desenha um explorador de perfil (a olhar para a direita) no frame ox."""
    y = respira  # 0 ou 1 píxel para baixo -> efeito de respiração
    # chapéu
    pygame.draw.rect(s, CHAPEU, (ox + 9, 3 + y, 14, 4))
    pygame.draw.rect(s, CHAPEU, (ox + 7, 7 + y, 19, 2))
    # cabeça e olho
    pygame.draw.rect(s, PELE, (ox + 10, 9 + y, 12, 7))
    pygame.draw.rect(s, OLHO, (ox + 18, 11 + y, 2, 2))
    # tronco
    pygame.draw.rect(s, CAMISA, (ox + 10, 16 + y, 12, 8))
    # braço que balança com as pernas
    pygame.draw.rect(s, PELE, (ox + 14 - perna // 2, 18 + y, 3, 5))
    # pernas: perna em -2..2 afasta-as
    pygame.draw.rect(s, CALCAS, (ox + 11 + perna, 24, 4, 5))
    pygame.draw.rect(s, CALCAS, (ox + 17 - perna, 24, 4, 5))
    pygame.draw.rect(s, BOTAS, (ox + 11 + perna, 29, 5, 2))
    pygame.draw.rect(s, BOTAS, (ox + 17 - perna, 29, 5, 2))


def gerar_spritesheet() -> str:
    folha = pygame.Surface((F * 6, F), pygame.SRCALPHA)
    folha.fill((0, 0, 0, 0))  # fundo transparente
    desenhar_frame(folha, 0 * F, 0, 0)      # parado
    desenhar_frame(folha, 1 * F, 0, 1)      # parado (respira)
    for i, perna in enumerate((2, 0, -2, 0)):
        desenhar_frame(folha, (2 + i) * F, perna, 0)
    caminho = os.path.join(RAIZ, "assets", "sprites", "explorador.png")
    os.makedirs(os.path.dirname(caminho), exist_ok=True)
    pygame.image.save(folha, caminho)
    return caminho


def gerar_bip() -> str:
    caminho = os.path.join(RAIZ, "assets", "sounds", "teste.wav")
    os.makedirs(os.path.dirname(caminho), exist_ok=True)
    taxa, dur, freq = 44100, 0.3, 880
    with wave.open(caminho, "wb") as w:
        w.setnchannels(1)
        w.setsampwidth(2)
        w.setframerate(taxa)
        n = int(taxa * dur)
        amostras = (
            int(12000 * math.sin(2 * math.pi * freq * i / taxa) * (1 - i / n))
            for i in range(n)
        )
        w.writeframes(b"".join(struct.pack("<h", a) for a in amostras))
    return caminho


if __name__ == "__main__":
    pygame.init()
    print("Criado:", gerar_spritesheet())
    print("Criado:", gerar_bip())
    pygame.quit()
