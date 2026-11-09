"""Testes dos power-ups (efeitos e gerador), partículas e menu."""

import random

import pytest

from src import config
from src.entities.powerup import PowerUp
from src.systems.effects import ESCUDO, VELOCIDADE, VIDA, EfeitosActivos, GeradorPowerUps
from src.systems.particles import SistemaParticulas
from src.ui.menu import Menu


# -- efeitos ---------------------------------------------------------------------
def test_efeito_dura_o_tempo_certo():
    e = EfeitosActivos()
    e.activar(ESCUDO)
    assert e.update(config.DURACAO_ESCUDO - 0.1) == [] and e.activo(ESCUDO)
    assert e.update(0.2) == [ESCUDO] and not e.activo(ESCUDO)


def test_apanhar_outra_vez_renova_mas_nao_acumula():
    e = EfeitosActivos()
    e.activar(VELOCIDADE)
    e.update(4.0)
    e.activar(VELOCIDADE)
    assert e.restante[VELOCIDADE] == pytest.approx(config.DURACAO_VELOCIDADE)


def test_escudo_e_velocidade_em_simultaneo():
    e = EfeitosActivos()
    e.activar(ESCUDO)
    e.activar(VELOCIDADE)
    assert e.activo(ESCUDO) and e.activo(VELOCIDADE)


def test_fraccao_para_a_barra():
    e = EfeitosActivos()
    e.activar(ESCUDO)
    e.update(config.DURACAO_ESCUDO / 2)
    assert e.fraccao(ESCUDO) == pytest.approx(0.5)


# -- gerador ---------------------------------------------------------------------
def test_gerador_respeita_intervalo_e_so_um_de_cada_vez():
    g = GeradorPowerUps(random.Random(1))
    tempo, criado = 0.0, None
    while criado is None:
        criado = g.update(0.1, ja_existe=False)
        tempo += 0.1
    lo, hi = config.POWERUP_INTERVALO
    assert lo <= tempo <= hi + 0.1 and criado in (ESCUDO, VELOCIDADE, VIDA)
    # com um power-up no chão, o relógio não anda
    assert all(g.update(5.0, ja_existe=True) is None for _ in range(10))


def test_gerador_produz_os_tres_tipos():
    g = GeradorPowerUps(random.Random(3))
    tipos = set()
    for _ in range(20000):
        t = g.update(0.1, ja_existe=False)
        if t:
            tipos.add(t)
    assert tipos == {ESCUDO, VELOCIDADE, VIDA}


def test_powerup_expira_no_chao():
    p = PowerUp(ESCUDO, 100, 100)
    p.update(config.POWERUP_DURACAO_NO_CHAO - 0.1)
    assert not p.expirou
    p.update(0.2)
    assert p.expirou


# -- partículas --------------------------------------------------------------------
def test_particulas_nascem_movem_e_morrem():
    s = SistemaParticulas(random.Random(0))
    s.emitir(100, 100, 20, (1, 1, 1, 1), vida=0.5)
    assert len(s.particulas) == 20
    s.update(0.1)
    assert any((p.x, p.y) != (100, 100) for p in s.particulas)
    s.update(1.0)
    assert s.particulas == []


def test_particulas_tem_limite():
    s = SistemaParticulas(random.Random(0))
    s.emitir(0, 0, SistemaParticulas.LIMITE + 100, (1, 1, 1, 1))
    assert len(s.particulas) == SistemaParticulas.LIMITE


# -- menu ----------------------------------------------------------------------------
class InputFalso:
    """Imita o Input: define-se à mão o que foi carregado neste "frame"."""

    def __init__(self, carregadas=(), rato=(-1, -1), clique=None):
        self._c, self._rato, self.clique = set(carregadas), rato, clique

    def carregada(self, accao):
        return accao in self._c

    def rato(self):
        return self._rato


def menu_tres():
    return Menu.vertical([("A", "a"), ("B", "b"), ("C", "c")], 640, 300, espaco=80)


def test_teclado_navega_com_volta():
    m = menu_tres()
    m.update(InputFalso({"cima"}))
    assert m.seleccionado.accao == "c"          # do primeiro para o último
    m.update(InputFalso({"baixo"}))
    assert m.seleccionado.accao == "a"


def test_enter_activa_o_seleccionado():
    m = menu_tres()
    m.update(InputFalso({"baixo"}))
    assert m.update(InputFalso({"confirmar"})) == "b"


def test_rato_parado_ao_abrir_nao_rouba_a_seleccao():
    m = menu_tres()
    m.update(InputFalso(rato=(640, 460)))       # rato já estava em cima do "C"
    assert m.seleccionado.accao == "a"


def test_rato_por_cima_selecciona_e_clique_activa():
    m = menu_tres()
    m.update(InputFalso(rato=(0, 0)))            # posição inicial
    assert m.update(InputFalso(rato=(640, 460))) is None
    assert m.seleccionado.accao == "c"          # hover
    assert m.update(InputFalso(rato=(640, 380), clique=(640, 380))) == "b"


def test_clique_fora_dos_botoes_nao_faz_nada():
    m = menu_tres()
    assert m.update(InputFalso(rato=(10, 10), clique=(10, 10))) is None
