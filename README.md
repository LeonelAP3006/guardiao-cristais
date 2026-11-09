# Guardião dos Cristais

Jogo 2D de sobrevivência top-down desenvolvido em **Python + OpenGL** para o
Trabalho Prático Final de Computação Gráfica (Grupo 2 — Jogo 2D com Inteligência Artificial).

> Estado: **Bloco 1 concluído** — janela OpenGL, janela-visor sem distorção,
> transformações geométricas, texturas e sprite animado.

## Como executar (Windows / PowerShell)

```powershell
git clone https://github.com/<utilizador>/guardiao-cristais.git
cd guardiao-cristais
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
python tools\gerar_assets_teste.py     # só na primeira vez
python tools\verificar_ambiente.py     # deve terminar em "Tudo pronto!"
python main.py
```

Se o `Activate.ps1` for bloqueado:
`Set-ExecutionPolicy -Scope CurrentUser RemoteSigned`

## Controlos (demo actual)

| Acção | Tecla / rato |
|---|---|
| Mover | Setas ou WASD |
| Marcar ponto | Clique esquerdo |
| Sair | ESC |

## Testes

```powershell
python -m pytest
```

## Estrutura

```
main.py              ponto de entrada
src/config.py        constantes (resolução, FPS, cores)
src/engine/          tudo o que fala com o OpenGL: janela, renderer, texturas
src/core/            game loop (e, a seguir, cenas, input, assets, áudio)
src/scenes/          ecrãs do jogo (por agora só a cena de demonstração)
tools/               scripts auxiliares (verificar ambiente, gerar assets)
tests/               testes automáticos (pytest) da lógica sem OpenGL
assets/              sprites, sons, fontes + CREDITS.md
docs/                diagramas, capturas e relatório
```

## Tecnologias

- **Pygame** — janela, contexto OpenGL, eventos, áudio e leitura de PNG.
  Não é usado para desenhar.
- **PyOpenGL** — toda a renderização (projecção ortográfica, viewport,
  transformações, texturas).
- **SQLite** (biblioteca padrão) — ranking.
- **pytest** — testes.
