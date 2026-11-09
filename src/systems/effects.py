"""Power-ups: tipos, efeitos temporários activos e quando aparecem.

Regras de interacção (decisões de design, documentadas aqui e no relatório):
  - ESCUDO e VELOCIDADE podem estar activos AO MESMO TEMPO.
  - Apanhar um efeito que já está activo NÃO acumula: renova a duração
    (volta aos 5 s). Acumular tornava o jogo trivial com sorte.
  - VIDA é instantânea (não tem duração). Se as vidas já estão no máximo,
    dá pontos em vez de vida, para o power-up nunca ser "inútil".
  - Só existe UM power-up no chão de cada vez, e desaparece se ninguém
    o apanhar (pisca nos últimos segundos como aviso).
"""

import random

from src import config

ESCUDO = "escudo"
VELOCIDADE = "velocidade"
VIDA = "vida"

DURACOES = {ESCUDO: config.DURACAO_ESCUDO, VELOCIDADE: config.DURACAO_VELOCIDADE}
# Frame no spritesheet powerups.png e cor associada (HUD, partículas)
FRAME = {ESCUDO: 0, VELOCIDADE: 1, VIDA: 2}
COR = {ESCUDO: (0.4, 0.85, 1.0, 1.0), VELOCIDADE: (1.0, 0.85, 0.2, 1.0),
       VIDA: (1.0, 0.35, 0.45, 1.0)}
# Probabilidades relativas: a vida é mais rara (é a mais valiosa).
PESOS = {ESCUDO: 4, VELOCIDADE: 4, VIDA: 2}


class EfeitosActivos:
    """Temporizadores dos efeitos com duração."""

    def __init__(self):
        self.restante: dict[str, float] = {}

    def activar(self, tipo: str) -> None:
        self.restante[tipo] = DURACOES[tipo]          # renova, não acumula

    def activo(self, tipo: str) -> bool:
        return self.restante.get(tipo, 0.0) > 0

    def fraccao(self, tipo: str) -> float:
        """0..1 do tempo que falta (para as barras do HUD)."""
        return max(0.0, self.restante.get(tipo, 0.0)) / DURACOES[tipo]

    def update(self, dt: float) -> list[str]:
        """Desconta o tempo. Devolve os tipos que terminaram NESTE frame."""
        terminados = []
        for tipo in list(self.restante):
            self.restante[tipo] -= dt
            if self.restante[tipo] <= 0:
                del self.restante[tipo]
                terminados.append(tipo)
        return terminados


class GeradorPowerUps:
    """Decide QUANDO e QUAL power-up aparece. Não sabe ONDE (isso é da cena)."""

    def __init__(self, rng: random.Random):
        self.rng = rng
        self._agendar()

    def _agendar(self) -> None:
        self.espera = self.rng.uniform(*config.POWERUP_INTERVALO)

    def update(self, dt: float, ja_existe: bool) -> str | None:
        """Devolve o tipo a criar agora, ou None."""
        if ja_existe:
            return None                         # o relógio só corre com o chão vazio
        self.espera -= dt
        if self.espera > 0:
            return None
        self._agendar()
        tipos = list(PESOS)
        return self.rng.choices(tipos, weights=[PESOS[t] for t in tipos])[0]
