"""Testes do ranking SQLite (base em memória ou em ficheiro temporário)."""

import pytest

from src import config
from src.data.ranking import Ranking, limpar_nome


@pytest.fixture
def ranking():
    r = Ranking(":memory:")
    yield r
    r.fechar()


def test_ranking_vazio(ranking):
    assert ranking.top() == []
    assert ranking.posicao_para(100) == 1


def test_ordenado_por_pontos_decrescentes(ranking):
    for nome, pontos in [("Ana", 300), ("Bruno", 900), ("Carla", 500)]:
        ranking.registar(nome, pontos)
    assert [r.nome for r in ranking.top()] == ["Bruno", "Carla", "Ana"]


def test_limite_do_top(ranking):
    for i in range(15):
        ranking.registar(f"J{i}", i * 10)
    top = ranking.top()
    assert len(top) == config.TAMANHO_RANKING
    assert top[0].pontos == 140 and top[-1].pontos == 50


def test_empate_fica_quem_chegou_primeiro(ranking):
    ranking.registar("Primeiro", 500)
    ranking.registar("Segundo", 500)
    assert [r.nome for r in ranking.top()] == ["Primeiro", "Segundo"]


def test_registar_devolve_id_e_guarda_todos_os_campos(ranking):
    novo = ranking.registar("Leo", 1234, onda=3, cristais=20, duracao=95.5)
    r = ranking.top()[0]
    assert (r.id, r.nome, r.pontos, r.onda, r.cristais, r.duracao) == \
           (novo, "Leo", 1234, 3, 20, 95.5)
    assert len(r.data) >= 16            # "AAAA-MM-DD HH:MM:SS"


def test_posicao_para_nova_pontuacao(ranking):
    for p in (900, 500, 300):
        ranking.registar("x", p)
    assert ranking.posicao_para(1000) == 1
    assert ranking.posicao_para(400) == 3
    assert ranking.posicao_para(10) == 4


def test_persistencia_entre_execucoes(tmp_path):
    ficheiro = str(tmp_path / "sub" / "ranking.db")
    r1 = Ranking(ficheiro)
    r1.registar("Persistente", 777)
    r1.fechar()                          # "fechar o jogo"
    r2 = Ranking(ficheiro)               # "abrir o jogo outra vez"
    assert r2.top()[0].nome == "Persistente"
    r2.fechar()


def test_sql_injection_e_guardado_como_texto(ranking):
    malicioso = "x'); DROP TABLE ranking;--"
    ranking.registar(malicioso, 10)
    assert ranking.top()[0].nome == limpar_nome(malicioso)   # a tabela continua viva


@pytest.mark.parametrize("entrada,esperado", [
    ("  Leo  ", "Leo"), ("", "Anónimo"), ("   ", "Anónimo"),
    ("NomeMuitoMuitoComprido", "NomeMuitoMui"), ("Jo\x00ão", "João"),
])
def test_limpar_nome(entrada, esperado):
    assert limpar_nome(entrada) == esperado
