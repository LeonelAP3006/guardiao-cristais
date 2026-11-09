"""Testes do sistema de animação (sem OpenGL)."""

import pytest

from src.systems.animation import Animation, Animator


def test_avanca_frame_quando_passa_a_duracao():
    a = Animation([2, 3, 4], 0.1)
    a.update(0.05)
    assert a.frame == 2
    a.update(0.06)
    assert a.frame == 3


def test_loop_volta_ao_inicio():
    a = Animation([2, 3], 0.1)
    a.update(0.25)          # 2 trocas: 2 -> 3 -> 2
    assert a.frame == 2


def test_sem_loop_para_no_ultimo():
    a = Animation([7, 8, 9], 0.1, loop=False)
    a.update(1.0)
    assert a.frame == 9 and a.terminou


def test_mesmo_resultado_a_30_e_a_144_fps():
    lenta, rapida = Animation([0, 1, 2, 3], 0.11), Animation([0, 1, 2, 3], 0.11)
    for _ in range(30):
        lenta.update(1 / 30)        # 1 segundo a 30 FPS
    for _ in range(144):
        rapida.update(1 / 144)      # 1 segundo a 144 FPS
    assert lenta.frame == rapida.frame


def test_animator_nao_reinicia_a_mesma_animacao():
    an = Animator({"andar": Animation([2, 3, 4, 5], 0.1),
                   "parado": Animation([0, 1], 0.5)}, inicial="andar")
    an.update(0.15)
    an.tocar("andar")       # pedido repetido, como acontece em cada frame
    assert an.frame == 3


def test_animator_troca_e_reinicia():
    an = Animator({"andar": Animation([2, 3, 4, 5], 0.1),
                   "parado": Animation([0, 1], 0.5)}, inicial="parado")
    an.tocar("andar"); an.update(0.25)
    an.tocar("parado"); an.tocar("andar")
    assert an.frame == 2


def test_animacao_vazia_e_erro():
    with pytest.raises(ValueError):
        Animation([], 0.1)
