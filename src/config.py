"""Configuração global do jogo.

Todas as constantes "mágicas" ficam aqui, num único sítio.
Se alguém quiser mudar a resolução, o FPS ou uma velocidade,
altera este ficheiro e não precisa de procurar números pelo código.
"""

import pygame

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
COR_DEBUG_HITBOX = (0.2, 1.0, 0.3, 0.35)
COR_PAUSA_VEU = (0.0, 0.0, 0.0, 0.55)

# --- Caminhos ---------------------------------------------------------------
PASTA_ASSETS = "assets"

# --- Controlos --------------------------------------------------------------
# Cada acção pode ter várias teclas. O código do jogo pergunta pela ACÇÃO
# ("cima"), nunca pela tecla; mudar controlos é só mexer aqui.
TECLAS = {
    "cima": (pygame.K_w, pygame.K_UP),
    "baixo": (pygame.K_s, pygame.K_DOWN),
    "esquerda": (pygame.K_a, pygame.K_LEFT),
    "direita": (pygame.K_d, pygame.K_RIGHT),
    "pausa": (pygame.K_ESCAPE, pygame.K_p),
    "confirmar": (pygame.K_RETURN, pygame.K_SPACE),
    "debug": (pygame.K_F1,),
    "sair": (pygame.K_q,),
    # Só para campos de texto/menus: não usam letras, para que escrever
    # um nome com "p" ou "q" não pause nem feche o jogo.
    "voltar": (pygame.K_ESCAPE,),
    "enter": (pygame.K_RETURN, pygame.K_KP_ENTER),
    "apagar": (pygame.K_BACKSPACE,),
}

# --- Jogador ----------------------------------------------------------------
VELOCIDADE_JOGADOR = 260.0     # unidades de mundo por segundo
ESCALA_SPRITE = 3              # sprites de 32 px desenhados a 96 px
TAMANHO_FRAME = 32             # píxeis de cada frame no spritesheet
# Hitbox menor que o desenho: os píxeis transparentes à volta do boneco
# não devem contar como "corpo". Medida a partir do explorador.png.
JOGADOR_HITBOX = (48, 72)      # largura, altura (unidades de mundo)
DURACAO_FRAME_ANDAR = 0.11     # segundos por frame
DURACAO_FRAME_PARADO = 0.45

# --- Arena ------------------------------------------------------------------
ESPESSURA_PAREDE = 32

# --- Aleatoriedade ----------------------------------------------------------
# None = cada partida é diferente. Um número (ex.: 42) = cristais aparecem
# sempre nos mesmos sítios: útil para gravar o vídeo de demonstração.
SEMENTE = None

# --- Sessão: vidas, pontos, ondas -------------------------------------------
VIDAS_INICIAIS = 3
VIDAS_MAXIMO = 5
INVULNERAVEL_SEGUNDOS = 1.5    # imunidade depois de levar dano
PONTOS_CRISTAL = 100           # multiplicado pelo número da onda
PONTOS_POR_SEGUNDO = 10        # por sobreviver
BONUS_ONDA = 500
CRISTAIS_POR_ONDA = 8
AUMENTO_POR_ONDA = 0.10        # +10% de velocidade de inimigos e obstáculos
# Tecto do aumento: 165 x 1.5 = 247 < 260 (jogador). Sem tecto, a partir da
# onda 5 os inimigos ficavam mais rápidos que o jogador e fugir era impossível.
MULTIPLICADOR_MAXIMO = 1.5

# --- Inimigos (Sentinelas) --------------------------------------------------
INIMIGO_HITBOX = (52, 52)
INIMIGOS_INICIAIS = 2
INIMIGOS_MAXIMO = 6
VELOCIDADE_PATRULHA = 90.0
VELOCIDADE_PERSEGUICAO = 165.0  # menor que a do jogador: dá para fugir
RAIO_DETECCAO = 260.0
TEMPO_PARA_ESQUECER = 2.0       # segundos sem ver o jogador até desistir

# --- Power-ups --------------------------------------------------------------
POWERUP_TAMANHO = 40
POWERUP_INTERVALO = (10.0, 16.0)   # segundos entre aparições (sorteado)
POWERUP_DURACAO_NO_CHAO = 9.0      # desaparece se ninguém o apanhar
DURACAO_ESCUDO = 5.0
DURACAO_VELOCIDADE = 5.0
MULTIPLICADOR_VELOCIDADE = 1.6
PONTOS_VIDA_EXTRA_CHEIO = 250      # vida com vidas no máximo vira pontos

# --- Ranking ----------------------------------------------------------------
FICHEIRO_RANKING = "dados/ranking.db"
TAMANHO_RANKING = 10
NOME_MAXIMO = 12

# --- Áudio ------------------------------------------------------------------
VOLUME_MUSICA = 0.35
VOLUME_EFEITOS = 0.7

# --- Cristais ---------------------------------------------------------------
CRISTAL_TAMANHO = 36
DISTANCIA_MINIMA_CRISTAL = 180  # não aparece colado ao jogador
