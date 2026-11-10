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
| Menus | Setas/WASD + Enter, ou rato (passar por cima + clique) |
| Mover | Setas ou WASD |
| Pausar | ESC ou P (menu com Retomar, Reiniciar, Menu principal, Sair) |
| Modo de depuração: hitboxes e raio de visão da IA | F1 |
| Nome no Game Over | escrever, Backspace apaga, Enter grava, ESC não grava |

## Regras

- Recolhe **cristais** (100 pts × onda). Sobreviver dá +10 pts por segundo.
- A cada 8 cristais começa uma nova **onda**: +500 pts, mais uma sentinela,
  inimigos e obstáculos 10% mais rápidos (até ×1,5).
- **Sentinelas** patrulham; se te virem (raio + linha de visão) perseguem-te.
  Esconde-te atrás de um pilar e, passados 2 s, desistem.
- Tocar numa sentinela, numa **lâmina** ou num **laser** tira 1 vida.
  Ficas 1,5 s invulnerável (a piscar). Com 0 vidas: Game Over.
- **Power-ups** aparecem a cada 10-16 s e somem ao fim de 9 s:
  escudo (5 s sem dano), velocidade (5 s a 160%), vida (+1, máx. 5; com vidas
  cheias vale 250 pts). Apanhar o mesmo efeito outra vez renova a duração.
- No fim, escreve o nome: o resultado fica no **ranking** (Top 10, SQLite em
  `dados/ranking.db`, criado automaticamente).

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
src/core/            game loop, gestor de cenas, input, cache de assets, áudio
src/systems/         lógica sem OpenGL: colisão, animação, IA, sessão, spawn,
                     efeitos de power-up, partículas
src/entities/        objectos do jogo: jogador, sentinela, cristal, obstáculos,
                     power-up, arena
src/ui/              HUD e componente de menu (botões)
src/data/            ranking (SQLite)
src/scenes/          ecrãs: menu, como jogar, jogo, pausa, game over, ranking
tools/               verificar ambiente, gerar sprites e sons
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
