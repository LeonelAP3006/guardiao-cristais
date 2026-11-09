"""Ranking persistente com SQLite.

Porquê SQLite?
  - Vem com o Python (módulo sqlite3): zero instalações, zero servidores.
  - Guarda tudo num só ficheiro (dados/ranking.db) que sobrevive ao fecho do jogo.
  - Ordenar e limitar ("os 10 melhores") é uma linha de SQL, sem código manual.
  Alternativa considerada: um ficheiro JSON. Funciona, mas obriga a ler tudo,
  ordenar em Python e reescrever o ficheiro inteiro a cada resultado.

Modelo de dados (uma tabela):

    ranking
    ┌──────────┬─────────┬──────────────────────────────────────────┐
    │ id       │ INTEGER │ chave primária, gerada automaticamente   │
    │ nome     │ TEXT    │ nome do jogador (até 12 caracteres)      │
    │ pontos   │ INTEGER │ pontuação final                          │
    │ onda     │ INTEGER │ onda alcançada                           │
    │ cristais │ INTEGER │ cristais recolhidos                      │
    │ duracao  │ REAL    │ segundos sobrevividos                    │
    │ data     │ TEXT    │ data/hora local do registo               │
    └──────────┴─────────┴──────────────────────────────────────────┘

Segurança: TODAS as consultas usam parâmetros (?) e nunca juntam texto do
utilizador ao SQL. Um nome como  x'); DROP TABLE ranking;--  é guardado
literalmente como nome, sem executar nada (protecção contra SQL injection).
"""

import os
import sqlite3
from dataclasses import dataclass

from src import config

SQL_CRIAR = """
CREATE TABLE IF NOT EXISTS ranking (
    id       INTEGER PRIMARY KEY AUTOINCREMENT,
    nome     TEXT    NOT NULL,
    pontos   INTEGER NOT NULL,
    onda     INTEGER NOT NULL DEFAULT 1,
    cristais INTEGER NOT NULL DEFAULT 0,
    duracao  REAL    NOT NULL DEFAULT 0,
    data     TEXT    NOT NULL DEFAULT (datetime('now', 'localtime'))
);
CREATE INDEX IF NOT EXISTS idx_ranking_pontos ON ranking (pontos DESC);
"""

SQL_INSERIR = """
INSERT INTO ranking (nome, pontos, onda, cristais, duracao) VALUES (?, ?, ?, ?, ?)
"""

# Desempate: com os mesmos pontos, fica à frente quem chegou primeiro (id menor).
SQL_TOP = """
SELECT id, nome, pontos, onda, cristais, duracao, data
FROM ranking ORDER BY pontos DESC, id ASC LIMIT ?
"""

SQL_POSICAO = "SELECT COUNT(*) FROM ranking WHERE pontos > ?"


@dataclass
class Resultado:
    id: int
    nome: str
    pontos: int
    onda: int
    cristais: int
    duracao: float
    data: str


def limpar_nome(nome: str) -> str:
    """Remove espaços e caracteres de controlo, corta no máximo, nunca vazio."""
    nome = "".join(c for c in nome if c.isprintable()).strip()
    return nome[:config.NOME_MAXIMO] or "Anónimo"


class Ranking:

    def __init__(self, caminho: str = config.FICHEIRO_RANKING):
        """`caminho` = ficheiro .db, ou ":memory:" para testes (base temporária)."""
        if caminho != ":memory:":
            os.makedirs(os.path.dirname(caminho) or ".", exist_ok=True)
        self.ligacao = sqlite3.connect(caminho)
        self.ligacao.executescript(SQL_CRIAR)

    def registar(self, nome: str, pontos: int, onda: int = 1,
                 cristais: int = 0, duracao: float = 0.0) -> int:
        """Grava um resultado e devolve o seu id (para o destacar na tabela)."""
        with self.ligacao:                    # commit automático (ou rollback se falhar)
            cursor = self.ligacao.execute(
                SQL_INSERIR, (limpar_nome(nome), int(pontos), onda, cristais, duracao))
        return cursor.lastrowid

    def top(self, n: int = config.TAMANHO_RANKING) -> list[Resultado]:
        linhas = self.ligacao.execute(SQL_TOP, (n,)).fetchall()
        return [Resultado(*linha) for linha in linhas]

    def posicao_para(self, pontos: int) -> int:
        """Lugar (1 = primeiro) que esta pontuação ocuparia se fosse registada agora."""
        acima = self.ligacao.execute(SQL_POSICAO, (pontos,)).fetchone()[0]
        return acima + 1

    def fechar(self) -> None:
        self.ligacao.close()
