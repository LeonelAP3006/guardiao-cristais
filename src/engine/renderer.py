"""Primitivas de desenho 2D em OpenGL.

É o ÚNICO módulo (junto com window.py e texture.py) que faz chamadas de
desenho OpenGL. As cenas e entidades pedem "desenha este sprite aqui,
rodado X graus" e não sabem nada de glBegin/glVertex. Assim, se um dia
trocarmos o pipeline clássico por shaders, só este ficheiro muda.

Transformações geométricas (o coração do requisito):
  Cada objecto é desenhado CENTRADO NA ORIGEM (de -w/2 a +w/2) e depois
  movido para o sítio certo pela matriz MODELVIEW:

      M = T(x, y) · R(ângulo) · S(sx, sy)

  O OpenGL aplica-as ao vértice da direita para a esquerda:
  primeiro escala, depois roda (em torno do próprio centro), depois translada.
  Se transladássemos antes de rodar, o objecto rodaria em torno da origem
  do mundo (canto superior esquerdo), como um planeta em órbita.
"""

import math

from OpenGL.GL import (
    GL_QUADS, GL_TEXTURE_2D, GL_TRIANGLE_FAN,
    glBegin, glBindTexture, glColor4f, glDisable, glEnable, glEnd,
    glPopMatrix, glPushMatrix, glRotatef, glScalef, glTexCoord2f,
    glTranslatef, glVertex2f,
)

from src.engine.texture import Texture

Cor = tuple[float, float, float, float]
BRANCO: Cor = (1.0, 1.0, 1.0, 1.0)


class Renderer:

    # -- câmara ------------------------------------------------------------------
    @staticmethod
    def inicio_deslocamento(dx: float, dy: float) -> None:
        """Translada TUDO o que for desenhado a seguir (até fim_deslocamento).

        Usado no tremor de ecrã ao levar dano: em vez de mexer na posição
        de cada objecto, aplicamos UMA translação à cena inteira. É o mesmo
        glTranslate dos objectos, mas um nível acima na pilha de matrizes.
        """
        glPushMatrix()
        glTranslatef(dx, dy, 0.0)

    @staticmethod
    def fim_deslocamento() -> None:
        glPopMatrix()

    # -- transformação ---------------------------------------------------------
    @staticmethod
    def _transformar(cx: float, cy: float, angulo: float,
                     sx: float, sy: float) -> None:
        # glPushMatrix guarda a matriz actual; glPopMatrix (em quem chama)
        # restaura-a. Assim a transformação de um objecto não "contamina" o seguinte.
        glPushMatrix()
        glTranslatef(cx, cy, 0.0)          # T: leva o centro para (cx, cy)
        if angulo:
            glRotatef(angulo, 0.0, 0.0, 1.0)  # R: roda em torno do eixo Z (2D)
        if sx != 1.0 or sy != 1.0:
            glScalef(sx, sy, 1.0)          # S: escala; sx=-1 espelha na horizontal

    # -- formas geométricas ----------------------------------------------------
    def rect(self, cx: float, cy: float, w: float, h: float,
             cor: Cor = BRANCO, angulo: float = 0.0) -> None:
        """Rectângulo de cor sólida, centrado em (cx, cy)."""
        self._transformar(cx, cy, angulo, 1.0, 1.0)
        glColor4f(*cor)
        hw, hh = w / 2, h / 2
        # Um quad = 4 vértices, por ordem (sentido horário no nosso Y-para-baixo).
        glBegin(GL_QUADS)
        glVertex2f(-hw, -hh)
        glVertex2f(hw, -hh)
        glVertex2f(hw, hh)
        glVertex2f(-hw, hh)
        glEnd()
        glPopMatrix()

    def circulo(self, cx: float, cy: float, raio: float,
                cor: Cor = BRANCO, segmentos: int = 40) -> None:
        """Círculo aproximado por um leque de triângulos (TRIANGLE_FAN).

        O primeiro vértice é o centro; cada vértice seguinte forma um
        triângulo com o anterior e o centro. É também o melhor teste visual
        para a janela-visor: se o viewport distorcer, o círculo vira elipse.
        """
        self._transformar(cx, cy, 0.0, 1.0, 1.0)
        glColor4f(*cor)
        glBegin(GL_TRIANGLE_FAN)
        glVertex2f(0.0, 0.0)
        for i in range(segmentos + 1):
            a = 2 * math.pi * i / segmentos
            glVertex2f(math.cos(a) * raio, math.sin(a) * raio)
        glEnd()
        glPopMatrix()

    # -- sprites ----------------------------------------------------------------
    def sprite(self, textura: Texture, cx: float, cy: float, w: float, h: float,
               uv: tuple[float, float, float, float] = (0.0, 0.0, 1.0, 1.0),
               angulo: float = 0.0, espelhar_x: bool = False,
               cor: Cor = BRANCO) -> None:
        """Quad texturizado centrado em (cx, cy).

        uv     : rectângulo da textura a usar (um frame do spritesheet).
        cor    : multiplica a cor da textura ("tint"). (1,1,1,1) = original;
                 (1,0.3,0.3,1) = avermelhado (útil para o flash de dano);
                 alfa < 1 = semitransparente (piscar na invulnerabilidade).
        espelhar_x : escala -1 em x, para o personagem olhar para a esquerda
                     sem precisarmos de um segundo conjunto de imagens.
        """
        self._transformar(cx, cy, angulo, -1.0 if espelhar_x else 1.0, 1.0)
        glEnable(GL_TEXTURE_2D)
        glBindTexture(GL_TEXTURE_2D, textura.id)
        glColor4f(*cor)

        u0, v0, u1, v1 = uv
        hw, hh = w / 2, h / 2
        # Cada glTexCoord2f diz que ponto da imagem "cola" no vértice seguinte.
        glBegin(GL_QUADS)
        glTexCoord2f(u0, v0); glVertex2f(-hw, -hh)   # canto sup. esquerdo
        glTexCoord2f(u1, v0); glVertex2f(hw, -hh)    # canto sup. direito
        glTexCoord2f(u1, v1); glVertex2f(hw, hh)     # canto inf. direito
        glTexCoord2f(u0, v1); glVertex2f(-hw, hh)    # canto inf. esquerdo
        glEnd()

        glBindTexture(GL_TEXTURE_2D, 0)
        glDisable(GL_TEXTURE_2D)
        glPopMatrix()
