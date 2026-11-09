"""Testes dos obstáculos, colisão círculo-AABB, linha de visão e spawn."""

import math
import random

import pytest

from src import config
from src.entities.arena import LAMINAS, LASERS, PONTO_INICIAL, criar_paredes
from src.entities.obstacles import BarreiraLaser, LaminaRotativa
from src.entities.player import Player
from src.systems.collision import AABB, circulo_intersecta_aabb, linha_de_visao
from src.systems.spawn import posicao_livre


# -- círculo vs AABB --------------------------------------------------------------
def test_circulo_toca_aresta():
    assert circulo_intersecta_aabb(0, 0, 10, AABB(5, -5, 10, 10))


def test_circulo_perto_do_canto_mas_sem_tocar():
    # O canto está a sqrt(8^2+8^2) = 11.3 do centro: um raio 10 não chega.
    assert not circulo_intersecta_aabb(0, 0, 10, AABB(8, 8, 10, 10))


def test_centro_do_circulo_dentro_da_caixa():
    assert circulo_intersecta_aabb(5, 5, 1, AABB(0, 0, 10, 10))


# -- linha de visão -----------------------------------------------------------------
def test_linha_de_visao_livre_e_bloqueada():
    parede = AABB(50, -100, 20, 200)
    assert linha_de_visao((0, 0), (40, 0), [parede])
    assert not linha_de_visao((0, 0), (100, 0), [parede])


# -- obstáculos ---------------------------------------------------------------------
def test_lamina_roda_com_o_tempo_e_com_a_onda():
    a, b = LaminaRotativa(0, 0), LaminaRotativa(0, 0)
    a.update(0.5)
    b.update(0.5, multiplicador=2.0)
    assert a.angulo == pytest.approx(100) and b.angulo == pytest.approx(200)


def test_laser_fica_dentro_dos_limites():
    laser = BarreiraLaser(300, x_min=400, x_max=800)
    xs = []
    for _ in range(600):
        laser.update(1 / 60)
        xs.append(laser.caixa.centro[0])
    assert min(xs) >= 400 - 1 and max(xs) <= 800 + 1
    assert max(xs) - min(xs) > 350                  # percorre quase tudo


def test_ponto_inicial_sem_perigos():
    p = Player(*PONTO_INICIAL)
    obstaculos = [LaminaRotativa(x, y) for x, y in LAMINAS]
    obstaculos += [BarreiraLaser(y, fase=f) for y, f in LASERS]
    assert not any(o.zona_perigo().intersecta(p.caixa) for o in obstaculos)


# -- spawn ---------------------------------------------------------------------------
def test_posicao_livre_respeita_proibidas_e_distancia():
    rng = random.Random(1)
    paredes = criar_paredes()
    for _ in range(200):
        x, y = posicao_livre(rng, 40, paredes, longe_de=(640, 360), distancia_minima=180)
        caixa = AABB.a_partir_do_centro(x, y, 40, 40)
        assert not any(caixa.intersecta(p) for p in paredes)
        assert math.hypot(x - 640, y - 360) >= 180
        assert 0 < x < config.MUNDO_LARGURA and 0 < y < config.MUNDO_ALTURA


def test_mesma_semente_mesmas_posicoes():
    paredes = criar_paredes()
    a = [posicao_livre(random.Random(42), 40, paredes) for _ in range(3)]
    b = [posicao_livre(random.Random(42), 40, paredes) for _ in range(3)]
    assert a == b
