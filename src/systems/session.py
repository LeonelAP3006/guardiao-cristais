"""Estado de UMA partida: vidas, pontuação, onda e invulnerabilidade.

Juntámos "Life Manager" e "Score Manager" numa só classe porque partilham
o mesmo ciclo de vida (nascem e morrem com a partida) e interagem
(a onda muda os pontos de cada cristal). Separá-los obrigaria a passar
um para o outro sem ganho nenhum.

É lógica PURA: não desenha, não toca sons. Os métodos devolvem True/False
para a cena saber se deve reagir (som, partículas, Game Over...).

Protecção contra eventos repetidos:
  - Dano: o jogador fica em contacto com o inimigo durante VÁRIOS frames.
    Sem invulnerabilidade, perdia uma vida por frame (3 vidas em 0,05 s).
    Com ela, o 1.º contacto tira 1 vida e os seguintes são ignorados
    durante INVULNERAVEL_SEGUNDOS.
  - Cristal: a cena muda o cristal de sítio NO MESMO frame em que é
    recolhido, por isso não pode contar duas vezes.
"""

from src import config


class GameSession:

    def __init__(self):
        self.vidas = config.VIDAS_INICIAIS
        self.pontos = 0
        self.onda = 1
        self.cristais_na_onda = 0
        self.cristais_total = 0
        self.tempo_total = 0.0
        self.tempo_invulneravel = 0.0
        self._fraccao_segundo = 0.0

    # -- consultas -------------------------------------------------------------
    @property
    def invulneravel(self) -> bool:
        return self.tempo_invulneravel > 0

    @property
    def game_over(self) -> bool:
        return self.vidas <= 0

    @property
    def multiplicador_dificuldade(self) -> float:
        """1.0 na onda 1, 1.1 na onda 2, ... até ao máximo de 1.5."""
        return min(config.MULTIPLICADOR_MAXIMO,
                   1.0 + config.AUMENTO_POR_ONDA * (self.onda - 1))

    # -- tempo -------------------------------------------------------------------
    def update(self, dt: float) -> None:
        self.tempo_total += dt
        self.tempo_invulneravel = max(0.0, self.tempo_invulneravel - dt)
        # Pontos por sobrevivência: +10 a cada segundo COMPLETO. Acumulamos
        # as fracções de segundo para não perder tempo entre frames.
        self._fraccao_segundo += dt
        while self._fraccao_segundo >= 1.0:
            self._fraccao_segundo -= 1.0
            self.pontos += config.PONTOS_POR_SEGUNDO

    # -- eventos ------------------------------------------------------------------
    def sofrer_dano(self) -> bool:
        """Tira 1 vida. Devolve False (e não faz nada) se estiver protegido."""
        if self.invulneravel or self.game_over:
            return False
        self.vidas -= 1
        self.tempo_invulneravel = config.INVULNERAVEL_SEGUNDOS
        return True

    def recolher_cristal(self) -> bool:
        """Soma pontos. Devolve True se este cristal completou a onda."""
        self.pontos += config.PONTOS_CRISTAL * self.onda
        self.cristais_total += 1
        self.cristais_na_onda += 1
        if self.cristais_na_onda >= config.CRISTAIS_POR_ONDA:
            self.cristais_na_onda = 0
            self.onda += 1
            self.pontos += config.BONUS_ONDA
            return True
        return False

    def ganhar_vida(self) -> bool:
        """Para o power-up de vida (Bloco 4). False se já está no máximo."""
        if self.vidas >= config.VIDAS_MAXIMO:
            return False
        self.vidas += 1
        return True
