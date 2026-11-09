"""Inteligência Artificial dos inimigos: Máquina de Estados Finitos (FSM).

Porquê uma FSM e não algo mais sofisticado (A*, aprendizagem automática)?
  - O enunciado pede "IA simples".
  - Cada estado tem um comportamento claro e as transições são regras
    do tipo SE/ENTÃO, fáceis de explicar, testar e MOSTRAR no vídeo
    (com F1 o raio de detecção fica azul a patrulhar e vermelho a perseguir).

Estados e transições:

     ┌──────────┐  vê o jogador   ┌─────────────┐
     │ PATRULHA │ ──────────────▶ │ PERSEGUIÇÃO │ ◀─┐ vê o jogador
     └──────────┘                 └─────────────┘   │ (em qualquer estado)
          ▲                              │ não o vê há
          │ chegou à rota                │ TEMPO_PARA_ESQUECER s
          │                        ┌─────▼────┐
          └─────────────────────── │ RETORNO  │
                                   └──────────┘

"Ver o jogador" = estar a menos de RAIO_DETECCAO **e** haver linha de visão
(nenhuma parede pelo meio). Esconder-se atrás de um pilar funciona!

Na PERSEGUIÇÃO o inimigo vai para a ÚLTIMA POSIÇÃO ONDE VIU o jogador,
não para a posição real. Se o jogador se esconde, o inimigo vai ao sítio
onde o viu pela última vez e fica lá "à procura" até desistir.

Este módulo só DECIDE (direcção + velocidade). Mover e colidir é com a
entidade (entities/enemy.py). Assim testa-se a IA sem gráficos.
"""

import math

from src import config
from src.systems.collision import AABB, linha_de_visao

PATRULHA = "patrulha"
PERSEGUICAO = "perseguicao"
RETORNO = "retorno"

DISTANCIA_CHEGADA = 6.0   # "chegou" a um ponto se estiver a menos disto


def _distancia(a, b) -> float:
    return math.hypot(b[0] - a[0], b[1] - a[1])


class ControladorIA:

    def __init__(self, rota: list[tuple[float, float]],
                 raio_deteccao: float = config.RAIO_DETECCAO,
                 velocidade_patrulha: float = config.VELOCIDADE_PATRULHA,
                 velocidade_perseguicao: float = config.VELOCIDADE_PERSEGUICAO,
                 tempo_para_esquecer: float = config.TEMPO_PARA_ESQUECER):
        if not rota:
            raise ValueError("A rota de patrulha precisa de pelo menos 1 ponto")
        self.rota = rota
        self.raio = raio_deteccao
        self.vel_patrulha = velocidade_patrulha
        self.vel_perseguicao = velocidade_perseguicao
        self.tempo_para_esquecer = tempo_para_esquecer

        self.estado = PATRULHA
        self.indice = 0                       # próximo ponto da rota
        self.ultima_vista: tuple | None = None
        self.tempo_sem_ver = 0.0

    # -- percepção ------------------------------------------------------------
    def ve(self, pos, pos_jogador, paredes: list[AABB]) -> bool:
        return (_distancia(pos, pos_jogador) <= self.raio and
                linha_de_visao(pos, pos_jogador, paredes))

    def _ponto_da_rota_mais_proximo(self, pos) -> int:
        return min(range(len(self.rota)), key=lambda i: _distancia(pos, self.rota[i]))

    # -- decisão (chamada uma vez por frame) -----------------------------------
    def decidir(self, dt: float, pos, pos_jogador, paredes: list[AABB],
                multiplicador: float = 1.0) -> tuple[float, float, float]:
        """Devolve (dx, dy, velocidade): direcção unitária e rapidez."""

        # 1. TRANSIÇÕES ----------------------------------------------------------
        if self.ve(pos, pos_jogador, paredes):
            self.estado = PERSEGUICAO
            self.ultima_vista = pos_jogador
            self.tempo_sem_ver = 0.0
        elif self.estado == PERSEGUICAO:
            self.tempo_sem_ver += dt
            if self.tempo_sem_ver >= self.tempo_para_esquecer:
                self.estado = RETORNO
                self.indice = self._ponto_da_rota_mais_proximo(pos)

        # 2. COMPORTAMENTO DO ESTADO ACTUAL -----------------------------------
        if self.estado == PERSEGUICAO:
            destino, velocidade = self.ultima_vista, self.vel_perseguicao
        else:
            destino, velocidade = self.rota[self.indice], self.vel_patrulha
            if _distancia(pos, destino) < DISTANCIA_CHEGADA:
                if self.estado == RETORNO:
                    self.estado = PATRULHA          # voltou à rota
                self.indice = (self.indice + 1) % len(self.rota)
                destino = self.rota[self.indice]

        # 3. MOVIMENTO "POR DIRECÇÃO": vector unitário em direcção ao destino
        dx, dy = destino[0] - pos[0], destino[1] - pos[1]
        d = math.hypot(dx, dy)
        if d < DISTANCIA_CHEGADA:
            return 0.0, 0.0, 0.0                    # já está lá (à procura)
        return dx / d, dy / d, velocidade * multiplicador
