"""Menu de botões controlável por TECLADO e por RATO.

Teclado : ↑/↓ (ou W/S) muda a selecção; Enter/Espaço activa.
Rato    : passar por cima selecciona (hover); clique esquerdo activa.
Os dois modos partilham o mesmo "índice seleccionado", por isso nunca
há dois botões destacados ao mesmo tempo.

Detecção do rato: o ponto do rato (JÁ convertido para coordenadas do
mundo pelo Input, descontando as barras do letterbox) é testado contra
o rectângulo de cada botão. É a mesma AABB.contem da colisão.

O menu NÃO executa acções: update() devolve o nome da acção escolhida
("jogar", "sair"...) e a cena decide o que fazer. Assim o mesmo
componente serve para o menu principal, a pausa e o ranking.
"""

from src.systems.collision import AABB

COR_NORMAL = (0.16, 0.17, 0.28, 0.92)
COR_SELECCIONADO = (0.95, 0.75, 0.25, 1.0)
COR_BORDA = (0.45, 0.4, 0.6, 1.0)
COR_TEXTO = (0.9, 0.9, 1.0, 1.0)
COR_TEXTO_SELECCIONADO = (0.1, 0.08, 0.15, 1.0)


class Botao:

    def __init__(self, texto: str, accao: str, cx: float, cy: float,
                 largura: float = 360, altura: float = 60):
        self.texto = texto
        self.accao = accao
        self.caixa = AABB.a_partir_do_centro(cx, cy, largura, altura)


class Menu:

    def __init__(self, botoes: list[Botao]):
        self.botoes = botoes
        self.indice = 0
        self._rato_anterior = None

    @classmethod
    def vertical(cls, itens: list[tuple[str, str]], cx: float, y_inicial: float,
                 espaco: float = 76, largura: float = 360) -> "Menu":
        """Cria botões empilhados: itens = [(texto, accao), ...]."""
        return cls([Botao(t, a, cx, y_inicial + i * espaco, largura)
                    for i, (t, a) in enumerate(itens)])

    def update(self, inp) -> str | None:
        # Teclado (com volta: depois do último vem o primeiro)
        if inp.carregada("cima"):
            self.indice = (self.indice - 1) % len(self.botoes)
        if inp.carregada("baixo"):
            self.indice = (self.indice + 1) % len(self.botoes)

        # Rato: só muda a selecção se o rato se MEXEU, senão o rato parado
        # em cima de um botão "roubava" sempre a selecção feita com o teclado.
        rato = inp.rato()
        if self._rato_anterior is None:          # 1.º frame: só regista a posição
            self._rato_anterior = rato
        elif rato != self._rato_anterior:
            self._rato_anterior = rato
            for i, b in enumerate(self.botoes):
                if b.caixa.contem(*rato):
                    self.indice = i

        if inp.clique:
            for b in self.botoes:
                if b.caixa.contem(*inp.clique):
                    return b.accao
        if inp.carregada("confirmar"):
            return self.botoes[self.indice].accao
        return None

    @property
    def seleccionado(self) -> Botao:
        return self.botoes[self.indice]

    def render(self, r, texto) -> None:
        for i, b in enumerate(self.botoes):
            activo = i == self.indice
            cx, cy = b.caixa.centro
            r.rect(cx, cy, b.caixa.w + 6, b.caixa.h + 6,
                   COR_SELECCIONADO if activo else COR_BORDA)
            r.rect(cx, cy, b.caixa.w, b.caixa.h, COR_SELECCIONADO if activo else COR_NORMAL)
            texto.desenhar(r, b.texto, cx, cy + 2, 38,
                           COR_TEXTO_SELECCIONADO if activo else COR_TEXTO, alinhar="centro")
