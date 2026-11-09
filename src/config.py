"""Configuração global do jogo.

Todas as constantes "mágicas" ficam aqui, num único sítio.
Se alguém quiser mudar a resolução, o FPS ou uma velocidade,
altera este ficheiro e não precisa de procurar números pelo código.
"""

# --- Janela -----------------------------------------------------------------
TITULO = "Guardião dos Cristais"

# Tamanho inicial da janela, em píxeis do ecrã.
JANELA_LARGURA = 1280
JANELA_ALTURA = 720

# Tamanho do MUNDO virtual, em "unidades de mundo".
# O jogo é sempre desenhado neste espaço de 1280x720, independentemente
# do tamanho real da janela. A janela-visor faz a conversão (ver window.py).
MUNDO_LARGURA = 1280
MUNDO_ALTURA = 720

# --- Tempo ------------------------------------------------------------------
FPS_ALVO = 60
# Limite máximo do delta time (segundos). Se o jogo "engasgar" (por exemplo,
# ao arrastar a janela), um dt enorme faria os objectos saltar e atravessar
# paredes. Com este tecto, o pior caso é avançar 50 ms de cada vez.
DT_MAXIMO = 0.05

# --- Cores (R, G, B, A) no intervalo 0..1, como o OpenGL espera -------------
COR_BARRAS = (0.0, 0.0, 0.0, 1.0)        # letterbox fora da área de jogo
COR_FUNDO_ARENA = (0.12, 0.13, 0.20, 1.0)

# --- Caminhos ---------------------------------------------------------------
PASTA_ASSETS = "assets"
