"""Testes do jogador, do vector de direcção e da arena (sem janela)."""

import math

import pytest

from src import config
from src.core.input import vector_direccao
from src.entities.arena import PONTO_INICIAL, criar_paredes
from src.entities.player import Player
from src.systems.collision import AABB


# -- vector de direcção ----------------------------------------------------------
@pytest.mark.parametrize("teclas", [
    (False, True, False, False), (True, False, True, False), (False, True, False, True),
])
def test_direccao_tem_sempre_comprimento_1(teclas):
    assert math.hypot(*vector_direccao(*teclas)) == pytest.approx(1)


def test_teclas_opostas_anulam_se():
    assert vector_direccao(True, True, False, False) == (0, 0)


def test_cima_e_y_negativo():
    assert vector_direccao(False, False, True, False) == (0, -1)


# -- jogador -----------------------------------------------------------------------
def distancia_percorrida(fps: int, direccao=(1, 0)) -> float:
    p = Player(500, 300)
    x0 = p.posicao[0]
    for _ in range(fps):                 # 1 segundo de jogo
        p.update(1 / fps, direccao, [])
    return p.posicao[0] - x0


def test_velocidade_independente_do_fps():
    assert distancia_percorrida(30) == pytest.approx(distancia_percorrida(144))
    assert distancia_percorrida(60) == pytest.approx(config.VELOCIDADE_JOGADOR)


def test_diagonal_nao_e_mais_rapida():
    p = Player(500, 300)
    x0, y0 = p.posicao
    for _ in range(60):
        p.update(1 / 60, vector_direccao(False, True, False, True), [])
    x1, y1 = p.posicao
    assert math.hypot(x1 - x0, y1 - y0) == pytest.approx(config.VELOCIDADE_JOGADOR)


def test_estado_e_orientacao():
    p = Player(500, 300)
    p.update(1 / 60, (-1, 0), [])
    assert p.estado == "andar" and p.olha_esquerda
    p.update(1 / 60, (0, 0), [])
    assert p.estado == "parado" and p.olha_esquerda   # mantém para onde olhava


def test_nao_atravessa_parede():
    parede = AABB(600, 0, 32, 720)
    p = Player(500, 300)
    for _ in range(5 * 60):               # 5 s a andar para a direita
        p.update(1 / 60, (1, 0), [parede])
    assert p.caixa.direita == pytest.approx(600)


def test_dt_maximo_nao_causa_tunelling():
    parede = AABB(600, 0, config.ESPESSURA_PAREDE, 720)
    p = Player(560, 300)
    for _ in range(100):
        p.update(config.DT_MAXIMO, (1, 0), [parede])
    assert p.caixa.direita <= 600


# -- arena ---------------------------------------------------------------------------
def test_ponto_inicial_livre():
    p = Player(*PONTO_INICIAL)
    assert not any(p.caixa.intersecta(w) for w in criar_paredes())


def test_jogador_nunca_sai_da_arena():
    paredes = criar_paredes()
    for direccao in [(1, 0), (-1, 0), (0, 1), (0, -1), (0.7071, 0.7071)]:
        p = Player(*PONTO_INICIAL)
        for _ in range(10 * 60):
            p.update(1 / 60, direccao, paredes)
        assert 0 < p.caixa.esquerda and p.caixa.direita < config.MUNDO_LARGURA
        assert 0 < p.caixa.topo and p.caixa.fundo < config.MUNDO_ALTURA
