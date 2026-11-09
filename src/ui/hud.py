"""HUD (Heads-Up Display): vidas, pontuação, onda, progresso e power-ups activos.

Faixa de cima (sobre a parede): vidas, pontos, onda e cristais.
Faixa de baixo: um ícone e uma barra por cada power-up activo, que
encolhe à medida que o efeito acaba.
Lê o estado em cada frame, por isso a pontuação no ecrã muda no MESMO
frame em que o evento acontece ("pontuação dinâmica").
"""

from src import config
from src.systems.effects import COR, FRAME

ALTURA = config.ESPESSURA_PAREDE
Y = ALTURA / 2
Y_BAIXO = config.MUNDO_ALTURA - ALTURA / 2
COR_TEXTO = (1.0, 1.0, 1.0, 1.0)
COR_DESTAQUE = (1.0, 0.85, 0.3, 1.0)
FUNDO = (0.05, 0.05, 0.1, 0.75)


def desenhar_hud(r, texto, sessao, textura_coracao, efeitos=None, folha_powerups=None) -> None:
    W = config.MUNDO_LARGURA
    r.rect(W / 2, Y, W, ALTURA, FUNDO)

    # Vidas como ícones (imagens), não como número: lê-se de relance.
    for i in range(sessao.vidas):
        r.sprite(textura_coracao, 24 + i * 28, Y, 24, 24)

    texto.desenhar(r, f"PONTOS  {sessao.pontos}", W / 2, Y + 1, 30,
                   COR_DESTAQUE, alinhar="centro")
    texto.desenhar(r, f"ONDA {sessao.onda}    CRISTAIS {sessao.cristais_na_onda}/"
                      f"{config.CRISTAIS_POR_ONDA}",
                   W - 16, Y + 1, 26, COR_TEXTO, alinhar="direita")

    if not efeitos or not efeitos.restante:
        return
    r.rect(W / 2, Y_BAIXO, W, ALTURA, FUNDO)
    x = 24
    for tipo in sorted(efeitos.restante):
        r.sprite(folha_powerups.textura, x, Y_BAIXO, 26, 26, uv=folha_powerups.uv(FRAME[tipo]))
        largura = 140 * efeitos.fraccao(tipo)
        r.rect(x + 24 + 70, Y_BAIXO, 140, 10, (0.2, 0.2, 0.3, 1))       # fundo da barra
        r.rect(x + 24 + largura / 2, Y_BAIXO, largura, 10, COR[tipo])  # tempo restante
        texto.desenhar(r, tipo.upper(), x + 24 + 150, Y_BAIXO + 1, 22, COR[tipo])
        x += 330
