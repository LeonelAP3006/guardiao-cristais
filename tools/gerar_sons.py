"""Gera os efeitos sonoros e a música do jogo (síntese simples, sem direitos de terceiros).

Executar:  python tools/gerar_sons.py

Um som digital é uma sequência de AMOSTRAS (44100 por segundo), cada uma
um número entre -32768 e 32767 que diz a posição da membrana da coluna.
Aqui geramos as amostras com fórmulas:
  - onda quadrada  : sinal(sen(2πft))  -> som "chiptune" de consola antiga
  - onda triangular: mais suave, para a melodia
  - ruído          : valores aleatórios -> explosões, impactos
  - envolvente     : volume que decai com o tempo (o som "morre" naturalmente)
É o mesmo princípio de "imagem digital = matriz de píxeis", aplicado ao som.
"""

import math
import os
import random
import struct
import wave

RAIZ = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
PASTA = os.path.join(RAIZ, "assets", "sounds")
TAXA = 44100


def quadrada(f, t):
    return 1.0 if math.sin(2 * math.pi * f * t) >= 0 else -1.0


def triangular(f, t):
    return 2 * abs(2 * ((f * t) % 1) - 1) - 1


def tom(f_inicio, f_fim, duracao, forma=quadrada, volume=0.35, decai=True):
    """Tom com frequência que desliza de f_inicio a f_fim (glissando)."""
    n = int(TAXA * duracao)
    fase, saida = 0.0, []
    for i in range(n):
        p = i / n
        f = f_inicio + (f_fim - f_inicio) * p
        fase += f / TAXA                             # integrar a frequência
        env = (1 - p) ** 1.5 if decai else min(1, (1 - p) * 8)
        saida.append(forma(1, fase) * volume * env)
    return saida


def ruido(duracao, volume=0.4, rng=random.Random(7)):
    n = int(TAXA * duracao)
    return [rng.uniform(-1, 1) * volume * (1 - i / n) ** 2 for i in range(n)]


def silencio(duracao):
    return [0.0] * int(TAXA * duracao)


def misturar(*faixas):
    n = max(len(f) for f in faixas)
    return [sum(f[i] for f in faixas if i < len(f)) for i in range(n)]


def guardar(nome, amostras):
    os.makedirs(PASTA, exist_ok=True)
    caminho = os.path.join(PASTA, nome)
    with wave.open(caminho, "wb") as w:
        w.setnchannels(1)
        w.setsampwidth(2)
        w.setframerate(TAXA)
        w.writeframes(b"".join(
            struct.pack("<h", int(max(-1, min(1, a)) * 32767)) for a in amostras))
    print("Criado:", caminho)


def nota(n):
    """Frequência da nota MIDI n (69 = Lá 440 Hz)."""
    return 440.0 * 2 ** ((n - 69) / 12)


def gerar_efeitos():
    # Cristal: arpejo rápido a subir (som "positivo")
    guardar("cristal.wav", sum((tom(nota(n), nota(n), 0.06, volume=0.3)
                                for n in (76, 81, 88)), []))
    # Dano: ruído + tom grave a descer (som "negativo")
    guardar("dano.wav", misturar(ruido(0.25, 0.35), tom(220, 70, 0.3, volume=0.35)))
    # Power-up: varrimento ascendente longo
    guardar("powerup.wav", tom(300, 1400, 0.35, triangular, 0.5))
    # Nova onda: pequena fanfarra
    guardar("onda.wav", sum((tom(nota(n), nota(n), d, volume=0.3)
                             for n, d in ((72, .09), (76, .09), (79, .09), (84, .3))), []))
    # Game Over: notas a descer, mais lentas
    guardar("gameover.wav", sum((tom(nota(n), nota(n) * 0.98, 0.28, triangular, 0.5)
                                 for n in (67, 63, 60, 55)), []))
    # Clique do menu: muito curto
    guardar("clique.wav", tom(900, 600, 0.04, volume=0.25))


def gerar_musica():
    """Ciclo de 8 compassos: baixo em quadrada + melodia em triangular (~13 s)."""
    batida = 0.2                                     # segundos por colcheia (150 BPM)
    acordes = [57, 53, 48, 55]                       # Lá m, Fá, Dó, Sol (graves)
    melodia = [69, 72, 76, 74, 72, 69, 67, 69,  65, 69, 72, 70, 69, 65, 64, 65,
               64, 67, 72, 71, 69, 67, 64, 67,  62, 67, 71, 69, 67, 71, 74, 76]
    baixo, voz = [], []
    for compasso in range(8):
        raiz = acordes[compasso % 4]
        for passo in range(8):
            n = raiz if passo % 2 == 0 else raiz + 12
            baixo += tom(nota(n), nota(n), batida, quadrada, 0.10)
        for passo in range(8):
            n = melodia[(compasso % 4) * 8 + passo]
            if compasso >= 4 and passo % 4 == 3:
                voz += silencio(batida)              # variação na 2.ª metade
            else:
                voz += tom(nota(n), nota(n), batida, triangular, 0.16)
    guardar("musica.wav", misturar(baixo, voz))


if __name__ == "__main__":
    gerar_efeitos()
    gerar_musica()
