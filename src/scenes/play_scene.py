"""Cena principal do jogo: junta todas as entidades e sistemas.

Ordem dentro de update() (a ordem importa!):
  1. input da cena (pausa, debug)
  2. sessão (tempo, invulnerabilidade, pontos por segundo)
  3. jogador (move-se primeiro: os inimigos reagem à posição NOVA)
  4. inimigos (IA decide e move-se), obstáculos, cristal
  5. colisões entre entidades -> eventos: dano, cristal recolhido
  6. consequências: nova onda, Game Over

A cena é o "árbitro": as entidades não se conhecem umas às outras.
O jogador não sabe que existem inimigos; é a cena que pergunta
"a caixa do jogador toca na do inimigo?" e decide o que acontece.
Isto evita dependências cruzadas e facilita o trabalho em paralelo.
"""

import math
import random

from src import config
from src.core.scene_manager import Scene
from src.entities.arena import LAMINAS, LASERS, PONTO_INICIAL, ROTAS_PATRULHA, Arena
from src.entities.crystal import Cristal
from src.entities.enemy import Sentinela, separar_inimigos
from src.entities.obstacles import BarreiraLaser, LaminaRotativa
from src.entities.player import Player
from src.scenes.pause_scene import PauseScene
from src.systems.session import GameSession
from src.systems.spawn import posicao_livre
from src.ui.hud import desenhar_hud


class PlayScene(Scene):

    def on_enter(self) -> None:
        a = self.game.assets
        self.rng = random.Random(config.SEMENTE)
        self.sessao = GameSession()
        self.mostrar_debug = False

        self.arena = Arena(a.textura("parede", repetir=True))
        self.jogador = Player(*PONTO_INICIAL, folha=a.folha("explorador"))
        self.obstaculos = [LaminaRotativa(x, y, a.folha("lamina")) for x, y in LAMINAS]
        self.obstaculos += [BarreiraLaser(y, fase=f) for y, f in LASERS]

        self.inimigos: list[Sentinela] = []
        for _ in range(config.INIMIGOS_INICIAIS):
            self._adicionar_inimigo()

        self.cristal = Cristal(0, 0, a.folha("cristal"))
        self._reposicionar_cristal()
        self.tex_coracao = a.textura("coracao")

    # -- auxiliares -------------------------------------------------------------
    def _adicionar_inimigo(self) -> None:
        """Nova sentinela na rota livre cujo ponto inicial está mais LONGE do jogador.

        Assim nunca aparece um inimigo em cima do jogador numa mudança de onda.
        """
        usadas = [s.rota for s in self.inimigos]
        livres = [r for r in ROTAS_PATRULHA if r not in usadas]
        if not livres:
            return
        jx, jy = self.jogador.posicao
        rota = max(livres, key=lambda r: math.hypot(r[0][0] - jx, r[0][1] - jy))
        self.inimigos.append(Sentinela(rota, self.game.assets.folha("sentinela")))

    def _reposicionar_cristal(self) -> None:
        proibidas = self.arena.paredes + [o.zona_perigo() for o in self.obstaculos]
        x, y = posicao_livre(self.rng, config.CRISTAL_TAMANHO + 16, proibidas,
                             longe_de=self.jogador.posicao,
                             distancia_minima=config.DISTANCIA_MINIMA_CRISTAL)
        self.cristal.mover_para(x, y)

    # -- ciclo ----------------------------------------------------------------
    def update(self, dt: float) -> None:
        inp = self.game.input
        if inp.carregada("pausa"):
            self.manager.push(PauseScene())
            return
        if inp.carregada("debug"):
            self.mostrar_debug = not self.mostrar_debug

        s = self.sessao
        mult = s.multiplicador_dificuldade
        s.update(dt)

        paredes = self.arena.paredes
        self.jogador.update(dt, inp.direccao(), paredes)
        for inimigo in self.inimigos:
            inimigo.update(dt, self.jogador.posicao, paredes, mult)
        separar_inimigos(self.inimigos, paredes, dt)
        for obstaculo in self.obstaculos:
            obstaculo.update(dt, mult)
        self.cristal.update(dt)

        self._colisoes()

        if s.game_over:
            from src.scenes.game_over_scene import GameOverScene   # evita import circular
            self.manager.replace(GameOverScene(s))

    def _colisoes(self) -> None:
        caixa = self.jogador.caixa
        s = self.sessao

        # Cristal: soma pontos e muda de sítio NO MESMO frame (não conta 2 vezes).
        if caixa.intersecta(self.cristal.caixa):
            nova_onda = s.recolher_cristal()
            self._reposicionar_cristal()
            if nova_onda and len(self.inimigos) < config.INIMIGOS_MAXIMO:
                self._adicionar_inimigo()

        # Perigos: um só teste de dano por frame; a sessão ignora se invulnerável.
        atingido = (any(caixa.intersecta(i.caixa) for i in self.inimigos) or
                    any(o.toca(caixa) for o in self.obstaculos))
        if atingido:
            s.sofrer_dano()

    # -- desenho ---------------------------------------------------------------
    def render(self, r) -> None:
        # Ordem = profundidade: o que é desenhado depois fica por cima.
        if self.mostrar_debug:
            for inimigo in self.inimigos:
                inimigo.render_debug(r)
        for obstaculo in self.obstaculos:
            obstaculo.render(r)
        self.cristal.render(r)
        for inimigo in self.inimigos:
            inimigo.render(r)
        self.jogador.render(r, self.sessao.tempo_invulneravel)
        self.arena.render(r)       # paredes por cima: "tapam" a cabeça junto a elas

        if self.mostrar_debug:
            caixas = [self.jogador.caixa, self.cristal.caixa]
            caixas += [i.caixa for i in self.inimigos]
            caixas += [o.caixa for o in self.obstaculos if isinstance(o, BarreiraLaser)]
            for c in caixas:
                r.rect(*c.centro, c.w, c.h, config.COR_DEBUG_HITBOX)
            for o in self.obstaculos:
                if isinstance(o, LaminaRotativa):
                    r.circulo(o.cx, o.cy, o.raio_colisao, config.COR_DEBUG_HITBOX)

        desenhar_hud(r, self.game.texto, self.sessao, self.tex_coracao)
