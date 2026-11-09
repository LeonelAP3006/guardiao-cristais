"""Testes de comportamento da IA (máquina de estados)."""

import math

import pytest

from src.entities.arena import ROTAS_PATRULHA, criar_paredes
from src.entities.enemy import Sentinela, separar_inimigos
from src.systems.ai import PATRULHA, PERSEGUICAO, RETORNO, ControladorIA
from src.systems.collision import AABB

ROTA = [(100, 100), (300, 100)]
LONGE = (1000, 600)


def test_comeca_em_patrulha():
    assert ControladorIA(ROTA).estado == PATRULHA


def test_patrulha_vai_para_o_proximo_ponto():
    ia = ControladorIA(ROTA)
    dx, dy, vel = ia.decidir(0.016, (100, 100), LONGE, [])
    # estava no ponto 0 -> segue para o ponto 1, que fica à direita
    assert (dx, dy) == pytest.approx((1, 0)) and vel == ia.vel_patrulha


def test_ve_jogador_dentro_do_raio_e_persegue():
    ia = ControladorIA(ROTA, raio_deteccao=200)
    dx, dy, vel = ia.decidir(0.016, (100, 100), (100, 250), [])
    assert ia.estado == PERSEGUICAO
    assert (dx, dy) == pytest.approx((0, 1)) and vel == ia.vel_perseguicao


def test_fora_do_raio_nao_ve():
    ia = ControladorIA(ROTA, raio_deteccao=200)
    ia.decidir(0.016, (100, 100), (100, 400), [])
    assert ia.estado == PATRULHA


def test_parede_pelo_meio_bloqueia_a_visao():
    ia = ControladorIA(ROTA, raio_deteccao=300)
    pilar = AABB(80, 160, 40, 40)                    # entre o inimigo e o jogador
    ia.decidir(0.016, (100, 100), (100, 250), [pilar])
    assert ia.estado == PATRULHA


def test_esquece_depois_do_tempo_e_volta_a_rota():
    ia = ControladorIA(ROTA, raio_deteccao=200, tempo_para_esquecer=2.0)
    ia.decidir(0.016, (100, 100), (100, 250), [])
    assert ia.estado == PERSEGUICAO
    fora_da_rota = (200, 250)
    ia.decidir(1.0, fora_da_rota, LONGE, [])
    assert ia.estado == PERSEGUICAO                  # ainda à procura
    ia.decidir(1.1, fora_da_rota, LONGE, [])
    assert ia.estado == RETORNO
    # chegou a um ponto da rota -> volta a patrulhar
    ia.decidir(0.016, (100, 100), LONGE, [])
    assert ia.estado == PATRULHA


def test_vai_a_ultima_posicao_vista():
    ia = ControladorIA(ROTA, raio_deteccao=200)
    ia.decidir(0.016, (100, 100), (250, 100), [])   # viu à direita
    dx, dy, _ = ia.decidir(0.016, (100, 100), LONGE, [])  # deixou de ver
    assert (dx, dy) == pytest.approx((1, 0))        # continua para onde o viu


def test_multiplicador_aumenta_velocidade():
    ia = ControladorIA(ROTA)
    _, _, normal = ia.decidir(0.016, (100, 100), LONGE, [], 1.0)
    _, _, rapido = ia.decidir(0.016, (100, 100), LONGE, [], 1.5)
    assert rapido == pytest.approx(normal * 1.5)


def test_sentinela_aproxima_se_do_jogador():
    paredes = criar_paredes()
    s = Sentinela(ROTAS_PATRULHA[0])
    jogador = (250, 250)            # dentro do raio e sem pilar pelo meio
    d0 = math.dist(s.posicao, jogador)
    for _ in range(60):
        s.update(1 / 60, jogador, paredes)
    assert s.em_alerta and math.dist(s.posicao, jogador) < d0


def test_separacao_afasta_inimigos_sobrepostos():
    paredes = criar_paredes()
    a, b = Sentinela([(600, 360)]), Sentinela([(610, 360)])
    assert a.caixa.intersecta(b.caixa)
    for _ in range(60):
        separar_inimigos([a, b], paredes, 1 / 60)
    assert not a.caixa.intersecta(b.caixa)


@pytest.mark.parametrize("rota", ROTAS_PATRULHA)
def test_rotas_nao_comecam_dentro_de_paredes(rota):
    s = Sentinela(rota)
    assert not any(s.caixa.intersecta(p) for p in criar_paredes())


@pytest.mark.parametrize("rota", ROTAS_PATRULHA)
def test_patrulha_completa_a_rota_sem_ficar_presa(rota):
    """Sem jogador por perto, a sentinela deve visitar todos os pontos."""
    paredes = criar_paredes()
    s = Sentinela(rota)
    visitados = set()
    for _ in range(60 * 30):                      # 30 s de jogo
        s.update(1 / 60, (-9999, -9999), paredes)
        visitados.add(s.ia.indice)
    assert visitados == set(range(len(rota)))
