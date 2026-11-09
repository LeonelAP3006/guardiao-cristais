"""Cena principal do jogo: junta todas as entidades e sistemas.

Ordem dentro de update() (a ordem importa!):
  1. input da cena (pausa, debug)
  2. temporizadores: sessão, efeitos de power-up, tremor
  3. jogador (move-se primeiro: os inimigos reagem à posição NOVA)
  4. inimigos (IA decide e move-se), obstáculos, cristal, power-up, partículas
  5. colisões entre entidades -> eventos: cristal, power-up, dano
  6. consequências: som, partículas, nova onda, Game Over

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
from src.entities.powerup import PowerUp
from src.scenes.pause_scene import PauseScene
from src.systems import effects
from src.systems.effects import ESCUDO, VELOCIDADE, VIDA, EfeitosActivos, GeradorPowerUps
from src.systems.particles import SistemaParticulas
from src.systems.session import GameSession
from src.systems.spawn import posicao_livre
from src.ui.hud import desenhar_hud

COR_CRISTAL = (0.4, 0.9, 1.0, 1.0)
COR_DANO = (1.0, 0.3, 0.3, 1.0)
DURACAO_TREMOR = 0.35
AMPLITUDE_TREMOR = 9.0


class PlayScene(Scene):

    def on_enter(self) -> None:
        a = self.game.assets
        self.rng = random.Random(config.SEMENTE)
        self.sessao = GameSession()
        self.efeitos = EfeitosActivos()
        self.gerador = GeradorPowerUps(self.rng)
        self.particulas = SistemaParticulas(self.rng)
        self.mostrar_debug = False
        self.tremor = 0.0
        self.tempo_rasto = 0.0

        self.arena = Arena(a.textura("parede", repetir=True))
        self.jogador = Player(*PONTO_INICIAL, folha=a.folha("explorador"))
        self.obstaculos = [LaminaRotativa(x, y, a.folha("lamina")) for x, y in LAMINAS]
        self.obstaculos += [BarreiraLaser(y, fase=f) for y, f in LASERS]

        self.inimigos: list[Sentinela] = []
        for _ in range(config.INIMIGOS_INICIAIS):
            self._adicionar_inimigo()

        self.cristal = Cristal(0, 0, a.folha("cristal"))
        self._reposicionar_cristal()
        self.powerup: PowerUp | None = None
        self.folha_powerups = a.folha("powerups")
        self.tex_coracao = a.textura("coracao")
        self.game.audio.musica(True)

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

    def _zonas_ocupadas(self):
        return self.arena.paredes + [o.zona_perigo() for o in self.obstaculos]

    def _reposicionar_cristal(self) -> None:
        x, y = posicao_livre(self.rng, config.CRISTAL_TAMANHO + 16, self._zonas_ocupadas(),
                             longe_de=self.jogador.posicao,
                             distancia_minima=config.DISTANCIA_MINIMA_CRISTAL)
        self.cristal.mover_para(x, y)

    def _criar_powerup(self, tipo: str) -> None:
        proibidas = self._zonas_ocupadas() + [self.cristal.caixa]
        x, y = posicao_livre(self.rng, config.POWERUP_TAMANHO + 16, proibidas,
                             longe_de=self.jogador.posicao, distancia_minima=150)
        self.powerup = PowerUp(tipo, x, y, self.folha_powerups)

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
        self.efeitos.update(dt)
        self.tremor = max(0.0, self.tremor - dt)

        # Efeito de velocidade: altera um ATRIBUTO do jogador, não o código dele.
        rapido = self.efeitos.activo(VELOCIDADE)
        self.jogador.velocidade = config.VELOCIDADE_JOGADOR * (
            config.MULTIPLICADOR_VELOCIDADE if rapido else 1.0)

        paredes = self.arena.paredes
        self.jogador.update(dt, inp.direccao(), paredes)
        for inimigo in self.inimigos:
            inimigo.update(dt, self.jogador.posicao, paredes, mult)
        separar_inimigos(self.inimigos, paredes, dt)
        for obstaculo in self.obstaculos:
            obstaculo.update(dt, mult)
        self.cristal.update(dt)
        self.particulas.update(dt)

        # Power-up: aparece de tempos a tempos, some se ninguém o apanhar.
        if self.powerup:
            self.powerup.update(dt)
            if self.powerup.expirou:
                self.powerup = None
        tipo_novo = self.gerador.update(dt, self.powerup is not None)
        if tipo_novo:
            self._criar_powerup(tipo_novo)

        # Rasto do power-up de velocidade (partículas atrás do jogador)
        if rapido and self.jogador.estado == "andar":
            self.tempo_rasto += dt
            while self.tempo_rasto > 0.03:
                self.tempo_rasto -= 0.03
                self.particulas.emitir(*self.jogador.posicao, 1, effects.COR[VELOCIDADE],
                                       velocidade=30, vida=0.35, tamanho=10)

        self._colisoes()

        if s.game_over:
            from src.scenes.game_over_scene import GameOverScene   # evita import circular
            self.manager.replace(GameOverScene(s))

    def _colisoes(self) -> None:
        caixa = self.jogador.caixa
        s, audio = self.sessao, self.game.audio

        # Cristal: soma pontos e muda de sítio NO MESMO frame (não conta 2 vezes).
        if caixa.intersecta(self.cristal.caixa):
            self.particulas.emitir(*self.cristal.caixa.centro, 22, COR_CRISTAL)
            nova_onda = s.recolher_cristal()
            self._reposicionar_cristal()
            audio.tocar("cristal")
            if nova_onda:
                audio.tocar("onda")
                self.particulas.emitir(*self.jogador.posicao, 60, (1, 0.85, 0.3, 1),
                                       velocidade=420, vida=0.9)
                if len(self.inimigos) < config.INIMIGOS_MAXIMO:
                    self._adicionar_inimigo()

        # Power-up: aplica o efeito e desaparece do chão.
        if self.powerup and caixa.intersecta(self.powerup.caixa):
            tipo = self.powerup.tipo
            if tipo == VIDA:
                if not s.ganhar_vida():
                    s.pontos += config.PONTOS_VIDA_EXTRA_CHEIO
            else:
                self.efeitos.activar(tipo)
            self.particulas.emitir(*self.powerup.caixa.centro, 26, effects.COR[tipo])
            audio.tocar("powerup")
            self.powerup = None

        # Perigos: um só teste de dano por frame; o escudo e a invulnerabilidade
        # (dentro da sessão) impedem perder várias vidas no mesmo contacto.
        if self.efeitos.activo(ESCUDO):
            return
        atingido = (any(caixa.intersecta(i.caixa) for i in self.inimigos) or
                    any(o.toca(caixa) for o in self.obstaculos))
        if atingido and s.sofrer_dano():
            audio.tocar("dano")
            self.particulas.emitir(*self.jogador.posicao, 30, COR_DANO, velocidade=300)
            self.tremor = DURACAO_TREMOR

    # -- desenho ---------------------------------------------------------------
    def render(self, r) -> None:
        # Tremor de ecrã: translação aleatória da cena inteira, a diminuir.
        dx = dy = 0.0
        if self.tremor > 0:
            forca = AMPLITUDE_TREMOR * self.tremor / DURACAO_TREMOR
            dx = self.rng.uniform(-forca, forca)
            dy = self.rng.uniform(-forca, forca)
        r.inicio_deslocamento(dx, dy)

        # Ordem = profundidade: o que é desenhado depois fica por cima.
        if self.mostrar_debug:
            for inimigo in self.inimigos:
                inimigo.render_debug(r)
        for obstaculo in self.obstaculos:
            obstaculo.render(r)
        self.cristal.render(r)
        if self.powerup:
            self.powerup.render(r)
        for inimigo in self.inimigos:
            inimigo.render(r)
        self.jogador.render(r, self.sessao.tempo_invulneravel)
        if self.efeitos.activo(ESCUDO):
            self._render_escudo(r)
        self.particulas.render(r)
        self.arena.render(r)       # paredes por cima: "tapam" a cabeça junto a elas

        if self.mostrar_debug:
            self._render_debug(r)
        r.fim_deslocamento()

        # O HUD fica FORA do deslocamento: não treme com a cena.
        desenhar_hud(r, self.game.texto, self.sessao, self.tex_coracao,
                     self.efeitos, self.folha_powerups)

    def _render_escudo(self, r) -> None:
        cx, cy = self.jogador.posicao
        pulso = 1 + 0.06 * math.sin(self.sessao.tempo_total * 10)
        restante = self.efeitos.restante.get(ESCUDO, 0)
        if restante < 1.5 and int(restante * 10) % 2:     # avisa que vai acabar
            return
        r.circulo(cx, cy, 58 * pulso, (0.4, 0.85, 1.0, 0.18))
        r.circulo(cx, cy, 50 * pulso, (0.6, 0.95, 1.0, 0.12))

    def _render_debug(self, r) -> None:
        caixas = [self.jogador.caixa, self.cristal.caixa]
        caixas += [i.caixa for i in self.inimigos]
        caixas += [o.caixa for o in self.obstaculos if isinstance(o, BarreiraLaser)]
        if self.powerup:
            caixas.append(self.powerup.caixa)
        for c in caixas:
            r.rect(*c.centro, c.w, c.h, config.COR_DEBUG_HITBOX)
        for o in self.obstaculos:
            if isinstance(o, LaminaRotativa):
                r.circulo(o.cx, o.cy, o.raio_colisao, config.COR_DEBUG_HITBOX)
