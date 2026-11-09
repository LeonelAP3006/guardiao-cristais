"""Testes de vidas, pontuação e ondas."""

import pytest

from src import config
from src.systems.session import GameSession


def test_estado_inicial():
    s = GameSession()
    assert (s.vidas, s.pontos, s.onda) == (config.VIDAS_INICIAIS, 0, 1)
    assert not s.game_over and not s.invulneravel


def test_dano_tira_uma_vida_e_da_invulnerabilidade():
    s = GameSession()
    assert s.sofrer_dano()
    assert s.vidas == config.VIDAS_INICIAIS - 1 and s.invulneravel


def test_contacto_continuo_tira_so_uma_vida():
    s = GameSession()
    for _ in range(30):                 # meio segundo encostado ao inimigo
        s.sofrer_dano()
        s.update(1 / 60)
    assert s.vidas == config.VIDAS_INICIAIS - 1


def test_invulnerabilidade_acaba():
    s = GameSession()
    s.sofrer_dano()
    s.update(config.INVULNERAVEL_SEGUNDOS + 0.01)
    assert not s.invulneravel
    assert s.sofrer_dano()


def test_game_over_com_zero_vidas():
    s = GameSession()
    for _ in range(config.VIDAS_INICIAIS):
        s.sofrer_dano()
        s.update(config.INVULNERAVEL_SEGUNDOS + 0.01)
    assert s.game_over and s.vidas == 0
    assert not s.sofrer_dano()          # não fica com vidas negativas


def test_pontos_por_sobrevivencia_nao_dependem_do_fps():
    a, b = GameSession(), GameSession()
    for _ in range(30 * 10):
        a.update(1 / 30)
    for _ in range(144 * 10):
        b.update(1 / 144)
    assert a.pontos == b.pontos == pytest.approx(10 * config.PONTOS_POR_SEGUNDO, abs=10)


def test_cristal_vale_mais_em_ondas_maiores():
    s = GameSession()
    s.recolher_cristal()
    assert s.pontos == config.PONTOS_CRISTAL
    s.onda = 3
    antes = s.pontos
    s.recolher_cristal()
    assert s.pontos - antes == 3 * config.PONTOS_CRISTAL


def test_onda_muda_ao_completar_cristais():
    s = GameSession()
    resultados = [s.recolher_cristal() for _ in range(config.CRISTAIS_POR_ONDA)]
    assert resultados[-1] is True and not any(resultados[:-1])
    assert s.onda == 2 and s.cristais_na_onda == 0
    esperado = config.CRISTAIS_POR_ONDA * config.PONTOS_CRISTAL + config.BONUS_ONDA
    assert s.pontos == esperado


def test_multiplicador_de_dificuldade():
    s = GameSession()
    assert s.multiplicador_dificuldade == pytest.approx(1.0)
    s.onda = 3
    assert s.multiplicador_dificuldade == pytest.approx(1 + 2 * config.AUMENTO_POR_ONDA)


def test_inimigos_nunca_ficam_mais_rapidos_que_o_jogador():
    s = GameSession()
    s.onda = 50
    assert s.multiplicador_dificuldade == pytest.approx(config.MULTIPLICADOR_MAXIMO)
    velocidade_max = config.VELOCIDADE_PERSEGUICAO * s.multiplicador_dificuldade
    assert velocidade_max < config.VELOCIDADE_JOGADOR


def test_vida_extra_tem_maximo():
    s = GameSession()
    s.vidas = config.VIDAS_MAXIMO
    assert not s.ganhar_vida() and s.vidas == config.VIDAS_MAXIMO
