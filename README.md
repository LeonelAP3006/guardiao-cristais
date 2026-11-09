# Guardião dos Cristais

Jogo 2D de sobrevivência top-down desenvolvido em **Python + OpenGL** para o
Trabalho Prático Final de Computação Gráfica (Grupo 2 — Jogo 2D com Inteligência Artificial).

> Estado: **Bloco 3 concluído** — jogo jogável do início ao Game Over: sentinelas
> com IA (patrulha, perseguição, retorno), cristais e pontuação, vidas com
> invulnerabilidade, lâminas e lasers animados, HUD e ondas de dificuldade.

## Como executar (Windows / PowerShell)

```powershell
git clone https://github.com/<utilizador>/guardiao-cristais.git
cd guardiao-cristais
python -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install -r requirements.txt
python tools\verificar_ambiente.py     # deve terminar em "Tudo pronto!"
python main.py
```

### Problemas comuns no Windows

| Erro | Solução |
|---|---|
| `Activate.ps1 cannot be loaded ... running scripts is disabled` | `Set-ExecutionPolicy -Scope CurrentUser RemoteSigned` (uma vez) |
| `Uma política de Controlo de Aplicações bloqueou este ficheiro` (pip.exe, pytest.exe) | Usar sempre `python -m pip ...` e `python -m pytest` |
| `import file mismatch` no pytest | Projecto duplicado numa subpasta com o mesmo nome; apagar a cópia |
| `GDI Generic` no verificar_ambiente | Actualizar o driver da placa gráfica |

## Controlos

| Acção | Tecla / rato |
|---|---|
| Mover | Setas ou WASD |
| Pausar / retomar | ESC ou P (retomar também com Enter, Espaço ou clique) |
| Sair (na pausa) | Q |
| Modo de depuração: hitboxes e raio de visão da IA | F1 |
| Jogar de novo (Game Over) | Enter ou clique |

## Regras

- Recolhe **cristais** (100 pts × onda). Sobreviver dá +10 pts por segundo.
- A cada 8 cristais começa uma nova **onda**: +500 pts, mais uma sentinela,
  inimigos e obstáculos 10% mais rápidos (até ×1,5).
- **Sentinelas** patrulham; se te virem (raio + linha de visão) perseguem-te.
  Esconde-te atrás de um pilar e, passados 2 s, desistem.
- Tocar numa sentinela, numa **lâmina** ou num **laser** tira 1 vida.
  Ficas 1,5 s invulnerável (a piscar). Com 0 vidas: Game Over.

> Para gravar o vídeo: em `src/config.py` mete `SEMENTE = 42`. Os cristais
> aparecem sempre nos mesmos sítios e a demonstração fica reproduzível.

## Testes

```powershell
python -m pytest
```

## Estrutura

```
main.py              ponto de entrada
src/config.py        constantes (resolução, FPS, cores)
src/engine/          tudo o que fala com o OpenGL: janela, renderer, texturas
src/core/            game loop, gestor de cenas, input, cache de assets
src/systems/         lógica sem OpenGL: colisão, animação, IA, sessão, spawn
src/entities/        objectos do jogo: jogador, sentinela, cristal, obstáculos, arena
src/ui/              HUD
src/scenes/          ecrãs do jogo: jogo, pausa, game over
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
