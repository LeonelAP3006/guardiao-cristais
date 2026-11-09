"""Power-up no chão: um ícone que pulsa e desaparece se não for apanhado."""

import math

from src import config
from src.systems.collision import AABB
from src.systems.effects import FRAME


class PowerUp:

    def __init__(self, tipo: str, cx: float, cy: float, folha=None):
        t = config.POWERUP_TAMANHO
        self.tipo = tipo
        self.caixa = AABB.a_partir_do_centro(cx, cy, t, t)
        self.folha = folha
        self.tempo = 0.0

    @property
    def expirou(self) -> bool:
        return self.tempo >= config.POWERUP_DURACAO_NO_CHAO

    def update(self, dt: float) -> None:
        self.tempo += dt

    def render(self, r) -> None:
        restante = config.POWERUP_DURACAO_NO_CHAO - self.tempo
        # Nos últimos 3 s pisca cada vez mais depressa: aviso de que vai sumir.
        if restante < 3 and int(self.tempo * (6 + (3 - restante) * 4)) % 2:
            return
        cx, cy = self.caixa.centro
        # ESCALA pulsante (seno): o ícone "respira" para chamar a atenção.
        escala = 1.0 + 0.12 * math.sin(self.tempo * 6)
        lado = config.TAMANHO_FRAME * 1.6 * escala
        r.sprite(self.folha.textura, cx, cy, lado, lado, uv=self.folha.uv(FRAME[self.tipo]))
