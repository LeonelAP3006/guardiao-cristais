"""HUD (Heads-Up Display): vidas, pontuação, onda e progresso, sempre visíveis.

Fica desenhado sobre a parede de cima, numa faixa escura semitransparente.
Lê o estado da GameSession em cada frame, por isso a pontuação no ecrã
muda no MESMO frame em que o evento acontece ("pontuação dinâmica").
"""

from src import config

ALTURA = config.ESPESSURA_PAREDE
Y = ALTURA / 2
COR_TEXTO = (1.0, 1.0, 1.0, 1.0)
COR_DESTAQUE = (1.0, 0.85, 0.3, 1.0)


def desenhar_hud(r, texto, sessao, textura_coracao) -> None:
    W = config.MUNDO_LARGURA
    r.rect(W / 2, Y, W, ALTURA, (0.05, 0.05, 0.1, 0.75))

    # Vidas como ícones (imagens), não como número: lê-se de relance.
    for i in range(sessao.vidas):
        r.sprite(textura_coracao, 24 + i * 28, Y, 24, 24)

    texto.desenhar(r, f"PONTOS  {sessao.pontos}", W / 2, Y + 1, 30,
                   COR_DESTAQUE, alinhar="centro")
    texto.desenhar(r, f"ONDA {sessao.onda}    CRISTAIS {sessao.cristais_na_onda}/"
                      f"{config.CRISTAIS_POR_ONDA}",
                   W - 16, Y + 1, 26, COR_TEXTO, alinhar="direita")
