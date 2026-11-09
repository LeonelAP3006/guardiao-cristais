"""Testes da janela-visor sem distorção (matemática pura, sem abrir janela)."""

import pytest

from src.engine.window import calcular_viewport, janela_para_mundo

MW, MH = 1280, 720


def test_janela_com_mesma_proporcao_nao_tem_barras():
    vp = calcular_viewport(1920, 1080, MW, MH)
    assert (vp.x, vp.y_topo, vp.largura, vp.altura) == (0, 0, 1920, 1080)
    assert vp.escala == pytest.approx(1.5)


def test_janela_quadrada_tem_barras_em_cima_e_em_baixo():
    vp = calcular_viewport(800, 800, MW, MH)
    assert vp.x == 0 and vp.largura == 800
    assert vp.altura == 450 and vp.y_topo == 175


def test_janela_larga_tem_barras_laterais():
    vp = calcular_viewport(1600, 600, MW, MH)
    assert vp.y_topo == 0 and vp.altura == 600
    assert vp.largura == 1067 and vp.x == 266


@pytest.mark.parametrize("w,h", [(800, 800), (1600, 600), (1280, 720), (333, 999)])
def test_proporcao_preservada(w, h):
    vp = calcular_viewport(w, h, MW, MH)
    assert vp.largura / vp.altura == pytest.approx(MW / MH, rel=0.01)
    assert vp.largura <= w and vp.altura <= h


def test_rato_no_centro_da_janela_e_centro_do_mundo():
    vp = calcular_viewport(800, 800, MW, MH)
    assert janela_para_mundo(400, 400, vp) == pytest.approx((640, 360))


def test_cantos_do_viewport_sao_cantos_do_mundo():
    vp = calcular_viewport(1600, 600, MW, MH)
    assert janela_para_mundo(vp.x, vp.y_topo, vp) == pytest.approx((0, 0))
    canto = janela_para_mundo(vp.x + vp.largura, vp.y_topo + vp.altura, vp)
    assert canto == pytest.approx((MW, MH), abs=1)
