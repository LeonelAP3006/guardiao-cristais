"""Escolha de posições livres para fazer aparecer objectos (cristais, power-ups)."""

import math
import random

from src import config
from src.systems.collision import AABB


def posicao_livre(rng: random.Random, tamanho: float, proibidas: list[AABB],
                  longe_de: tuple[float, float] | None = None,
                  distancia_minima: float = 0.0,
                  tentativas: int = 300) -> tuple[float, float]:
    """Centro aleatório onde uma caixa `tamanho` x `tamanho` não toca em nada proibido.

    Algoritmo de "tentativa e rejeição": sorteia um ponto, rejeita-o se
    colidir com uma zona proibida ou estiver perto demais do jogador,
    e repete. Numa arena maioritariamente livre encontra um ponto em
    poucas tentativas. `rng` é passado de fora para os testes (e o vídeo)
    poderem usar uma semente fixa e obter sempre o mesmo resultado.
    """
    margem = config.ESPESSURA_PAREDE + tamanho
    for _ in range(tentativas):
        cx = rng.uniform(margem, config.MUNDO_LARGURA - margem)
        cy = rng.uniform(margem, config.MUNDO_ALTURA - margem)
        caixa = AABB.a_partir_do_centro(cx, cy, tamanho, tamanho)
        if any(caixa.intersecta(p) for p in proibidas):
            continue
        if longe_de and math.hypot(cx - longe_de[0], cy - longe_de[1]) < distancia_minima:
            continue
        return cx, cy
    raise RuntimeError("Não foi encontrada nenhuma posição livre")
