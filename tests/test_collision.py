"""Testes da colisão AABB e da resolução por eixo."""

import pytest

from src.systems.collision import AABB, mover_com_colisao


# -- intersecção ---------------------------------------------------------------
def test_sobreposicao_e_colisao():
    assert AABB(0, 0, 10, 10).intersecta(AABB(5, 5, 10, 10))


def test_separados_nao_colidem():
    assert not AABB(0, 0, 10, 10).intersecta(AABB(20, 0, 10, 10))


def test_sobrepostos_so_num_eixo_nao_colidem():
    # mesma faixa vertical, mas um por cima do outro
    assert not AABB(0, 0, 10, 10).intersecta(AABB(0, 30, 10, 10))


def test_encostados_nao_colidem():
    # partilham a aresta x=10: encostar não é colisão
    assert not AABB(0, 0, 10, 10).intersecta(AABB(10, 0, 10, 10))


def test_um_dentro_do_outro_colide():
    assert AABB(0, 0, 100, 100).intersecta(AABB(40, 40, 5, 5))


# -- movimento com colisão -----------------------------------------------------
PAREDE_DIREITA = AABB(100, 0, 20, 200)


def test_movimento_livre_nao_e_alterado():
    caixa = AABB(0, 0, 10, 10)
    assert mover_com_colisao(caixa, 5, 7, [PAREDE_DIREITA]) == (False, False)
    assert (caixa.x, caixa.y) == (5, 7)


def test_bate_na_parede_e_fica_encostado():
    caixa = AABB(85, 50, 10, 10)
    bateu_x, _ = mover_com_colisao(caixa, 20, 0, [PAREDE_DIREITA])
    assert bateu_x
    assert caixa.direita == pytest.approx(PAREDE_DIREITA.esquerda)
    assert not caixa.intersecta(PAREDE_DIREITA)


def test_desliza_ao_longo_da_parede_na_diagonal():
    caixa = AABB(85, 50, 10, 10)
    mover_com_colisao(caixa, 20, 15, [PAREDE_DIREITA])
    assert caixa.direita == pytest.approx(100)   # X bloqueado
    assert caixa.y == pytest.approx(65)          # Y continuou: deslizou


def test_bater_vindo_de_baixo():
    tecto = AABB(0, 0, 200, 20)
    caixa = AABB(50, 25, 10, 10)
    _, bateu_y = mover_com_colisao(caixa, 0, -10, [tecto])
    assert bateu_y and caixa.topo == pytest.approx(20)


def test_canto_entre_duas_paredes():
    paredes = [AABB(100, 0, 20, 200), AABB(0, 100, 200, 20)]
    caixa = AABB(85, 85, 10, 10)
    mover_com_colisao(caixa, 30, 30, paredes)
    assert not any(caixa.intersecta(p) for p in paredes)
    assert (caixa.direita, caixa.fundo) == pytest.approx((100, 100))
