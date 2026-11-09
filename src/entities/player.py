"""O jogador: posição, movimento com colisão, estado e animação.

Fonte de verdade da posição = a HITBOX (self.caixa, uma AABB).
O sprite é só o desenho, centrado na hitbox. Assim a colisão nunca depende
do tamanho da imagem (que tem margens transparentes).

Estados do personagem (por agora):
    "parado" -> animação de respirar
    "andar"  -> animação de andar
Mais tarde: "atingido" (piscar), "morto".

O Player NÃO lê o teclado: recebe a direcção já calculada pela cena.
Isto permite testá-lo sem teclado (tests/test_player.py) e, se um dia
quisermos um comando ou uma repetição gravada, o Player não muda.
"""

from src import config
from src.systems.animation import Animation, Animator
from src.systems.collision import AABB, mover_com_colisao


class Player:

    def __init__(self, cx: float, cy: float, folha=None):
        largura, altura = config.JOGADOR_HITBOX
        self.caixa = AABB.a_partir_do_centro(cx, cy, largura, altura)
        self.folha = folha                       # SpriteSheet (None nos testes)
        self.velocidade = config.VELOCIDADE_JOGADOR   # power-ups vão alterar isto
        self.estado = "parado"
        self.olha_esquerda = False
        # Frames do explorador.png: 0-1 parado, 2-5 a andar.
        self.animator = Animator({
            "parado": Animation([0, 1], config.DURACAO_FRAME_PARADO),
            "andar": Animation([2, 3, 4, 5], config.DURACAO_FRAME_ANDAR),
        }, inicial="parado")

    @property
    def posicao(self) -> tuple[float, float]:
        """Centro do jogador. É isto que os inimigos vão perseguir."""
        return self.caixa.centro

    def update(self, dt: float, direccao: tuple[float, float],
               solidos: list[AABB]) -> None:
        dx, dy = direccao
        if dx or dy:
            self.estado = "andar"
            # deslocamento = direcção (comprimento 1) x velocidade x tempo
            mover_com_colisao(self.caixa,
                              dx * self.velocidade * dt,
                              dy * self.velocidade * dt,
                              solidos)
            if dx:
                self.olha_esquerda = dx < 0      # a ir só para cima/baixo mantém
        else:
            self.estado = "parado"

        self.animator.tocar(self.estado)
        self.animator.update(dt)

    def render(self, r, tempo_invulneravel: float = 0.0) -> None:
        cx, cy = self.caixa.centro
        tamanho = config.TAMANHO_FRAME * config.ESCALA_SPRITE

        # Efeitos visuais de dano, feitos só com a COR do quad (tint):
        cor = (1.0, 1.0, 1.0, 1.0)
        if tempo_invulneravel > 0:
            decorrido = config.INVULNERAVEL_SEGUNDOS - tempo_invulneravel
            if decorrido < 0.2:
                cor = (1.0, 0.25, 0.25, 1.0)         # flash vermelho ao ser atingido
            elif int(tempo_invulneravel * 12) % 2 == 0:
                cor = (1.0, 1.0, 1.0, 0.25)          # piscar = está invulnerável

        # -4: o boneco no PNG está ligeiramente abaixo do centro do frame;
        # sobe-se o desenho para que os pés coincidam com o fundo da hitbox.
        r.sprite(self.folha.textura, cx, cy - 4, tamanho, tamanho,
                 uv=self.folha.uv(self.animator.frame),
                 espelhar_x=self.olha_esquerda, cor=cor)
