"""Verifica se o PC está pronto para o projecto.  Cada membro deve correr:

    python tools/verificar_ambiente.py

Testa: versão do Python, bibliotecas, criação de janela OpenGL,
versão/placa OpenGL e áudio. Mostra [OK] ou [FALHA] com uma dica.
"""

import os
import sys

RAIZ = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
falhas = 0


def ok(msg):
    print(f"[OK]    {msg}")


def falha(msg, dica):
    global falhas
    falhas += 1
    print(f"[FALHA] {msg}\n        dica: {dica}")


# 1. Python
if sys.version_info >= (3, 10):
    ok(f"Python {sys.version.split()[0]}")
else:
    falha(f"Python {sys.version.split()[0]} é antigo", "instalar Python 3.12")

# 2. Bibliotecas
try:
    import pygame
    ok(f"pygame {pygame.version.ver} (SDL {'.'.join(map(str, pygame.get_sdl_version()))})")
except ImportError:
    falha("pygame não instalado", "activar a .venv e: pip install -r requirements.txt")
    sys.exit(1)
try:
    import OpenGL
    from OpenGL.GL import GL_RENDERER, GL_VENDOR, GL_VERSION, glGetString
    ok(f"PyOpenGL {OpenGL.__version__}")
except ImportError:
    falha("PyOpenGL não instalado", "pip install -r requirements.txt")
    sys.exit(1)

# 3. Janela + contexto OpenGL
pygame.init()
try:
    pygame.display.set_mode((320, 180), pygame.OPENGL | pygame.DOUBLEBUF)
    versao = glGetString(GL_VERSION).decode()
    ok("Janela OpenGL criada")
    ok(f"OpenGL {versao}")
    print(f"        placa: {glGetString(GL_RENDERER).decode()} ({glGetString(GL_VENDOR).decode()})")
    if "GDI Generic" in glGetString(GL_RENDERER).decode():
        falha("A usar o renderizador genérico do Windows (OpenGL 1.1)",
              "instalar/actualizar o driver da placa gráfica (Intel/AMD/NVIDIA)")
except Exception as erro:  # noqa: BLE001
    falha(f"Não foi possível criar contexto OpenGL: {erro}",
          "actualizar o driver gráfico; em máquina virtual activar aceleração 3D")

# 4. Áudio
try:
    pygame.mixer.init()
    som = pygame.mixer.Sound(os.path.join(RAIZ, "assets", "sounds", "teste.wav"))
    som.play()
    pygame.time.wait(400)
    ok("Áudio (deves ter ouvido um bip)")
except FileNotFoundError:
    falha("assets/sounds/teste.wav em falta", "python tools/gerar_assets_teste.py")
except Exception as erro:  # noqa: BLE001
    falha(f"Áudio indisponível: {erro}", "verificar dispositivo de som/colunas")

pygame.quit()
print("\nTudo pronto!" if falhas == 0 else f"\n{falhas} problema(s) encontrado(s).")
sys.exit(1 if falhas else 0)
