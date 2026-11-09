# Como contribuir

## Regras de ouro
1. A `main` tem de **executar sempre**. Nunca fazer push de código partido para a `main`.
2. Cada tarefa numa branch curta. Integrar várias vezes por dia.
3. Antes de integrar: `python -m pytest` e `python main.py` sem erros.
4. Só o `src/engine/` faz chamadas OpenGL. As cenas e entidades usam o `Renderer`.

## Branches
| Tipo | Nome | Exemplo |
|---|---|---|
| Funcionalidade | `feature/<tema>` | `feature/ia-inimigos` |
| Correcção | `fix/<problema>` | `fix/colisao-parede` |
| Documentação | `docs/<tema>` | `docs/relatorio-cap3` |

## Mensagens de commit
`<tipo>: <o que mudou, no presente>`
Tipos: `feat`, `fix`, `docs`, `test`, `refactor`, `chore`, `assets`.
Exemplo: `feat: inimigo persegue jogador dentro do raio de detecção`

## Fluxo diário
```powershell
git checkout main
git pull
git checkout -b feature/minha-tarefa
# ... trabalhar, testar ...
git add .
git commit -m "feat: descrição"
git pull --rebase origin main      # trazer o trabalho dos colegas
python -m pytest; python main.py  # testar outra vez depois do rebase
git push -u origin feature/minha-tarefa
# abrir Pull Request no GitHub -> outro membro revê -> merge
```

## Assets
Só imagens e sons **criados por nós** ou com licença **CC0/livre**.
Registar sempre a origem em `assets/CREDITS.md`.
