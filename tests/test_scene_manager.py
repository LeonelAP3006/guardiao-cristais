"""Testes do gestor de cenas (pilha)."""

from src.core.scene_manager import Scene, SceneManager


class CenaEspia(Scene):
    """Cena falsa que regista o que lhe acontece."""

    def __init__(self, nome, registo, transparente=False):
        super().__init__()
        self.nome, self.registo, self.transparente = nome, registo, transparente

    def on_enter(self): self.registo.append(f"entra {self.nome}")
    def on_exit(self): self.registo.append(f"sai {self.nome}")
    def update(self, dt): self.registo.append(f"update {self.nome}")
    def render(self, r): self.registo.append(f"render {self.nome}")


def test_so_o_topo_e_actualizado():
    reg = []
    sm = SceneManager()
    sm.push(CenaEspia("jogo", reg))
    sm.push(CenaEspia("pausa", reg, transparente=True))
    reg.clear()
    sm.update(0.016)
    assert reg == ["update pausa"]


def test_cena_transparente_desenha_a_de_baixo_primeiro():
    reg = []
    sm = SceneManager()
    sm.push(CenaEspia("jogo", reg))
    sm.push(CenaEspia("pausa", reg, transparente=True))
    reg.clear()
    sm.render(None)
    assert reg == ["render jogo", "render pausa"]


def test_cena_opaca_esconde_as_de_baixo():
    reg = []
    sm = SceneManager()
    sm.push(CenaEspia("jogo", reg))
    sm.push(CenaEspia("ranking", reg))
    reg.clear()
    sm.render(None)
    assert reg == ["render ranking"]


def test_pop_retoma_a_cena_anterior():
    reg = []
    sm = SceneManager()
    jogo = CenaEspia("jogo", reg)
    sm.push(jogo)
    sm.push(CenaEspia("pausa", reg))
    sm.pop()
    assert sm.topo is jogo and "sai pausa" in reg


def test_replace_esvazia_a_pilha():
    reg = []
    sm = SceneManager()
    sm.push(CenaEspia("jogo", reg))
    sm.push(CenaEspia("pausa", reg))
    sm.replace(CenaEspia("menu", reg))
    assert len(sm.pilha) == 1 and sm.topo.nome == "menu"
    assert reg[-3:] == ["sai pausa", "sai jogo", "entra menu"]
