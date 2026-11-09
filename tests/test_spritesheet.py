"""Testes do cálculo das coordenadas UV dos frames (sem OpenGL)."""

import pytest

from src.engine.texture import SpriteSheet


class TexturaFalsa:
    """Imita uma Texture só com o tamanho; não precisa de placa gráfica."""
    def __init__(self, largura, altura):
        self.largura, self.altura = largura, altura


def test_frames_numa_linha():
    folha = SpriteSheet(TexturaFalsa(192, 32), 32, 32)
    assert folha.total_frames == 6
    assert folha.uv(0) == pytest.approx((0, 0, 1 / 6, 1))
    assert folha.uv(5) == pytest.approx((5 / 6, 0, 1, 1))


def test_indice_da_volta():
    folha = SpriteSheet(TexturaFalsa(192, 32), 32, 32)
    assert folha.uv(6) == folha.uv(0)


def test_grelha_com_varias_linhas():
    folha = SpriteSheet(TexturaFalsa(64, 64), 32, 32)
    assert folha.uv(3) == pytest.approx((0.5, 0.5, 1, 1))
