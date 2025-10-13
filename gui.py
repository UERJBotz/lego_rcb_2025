from pybricks.tools import StopWatch, wait
from pybricks.parameters import Color

from cores import cor2Color, Cor
from comum import globais

_ = 0
H = 100

letras = {
    "A": [
        [ _, H, H, _, ], 
        [ H, _, _, H, ], 
        [ H, H, H, H, ], 
        [ H, _, _, H, ], 
        [ H, _, _, H, ],
    ],
    "M": [
        [ H, _, _, _, H, ],
        [ H, H, _, H, H, ],
        [ H, _, H, _, H, ],
        [ H, _, _, _, H, ],
        [ H, _, _, _, H, ],
    ],
    "V": [
        [ H, _, _, _, H, ],
        [ H, _, _, _, H, ],
        [ H, _, _, _, H, ],
        [ _, H, _, H, _, ],
        [ _, _, H, _, _, ],
    ],
    "Z": [
        [ H, H, H, H, ],
        [ _, _, _, H, ],
        [ _, _, H, _, ],
        [ _, H, _, _, ],
        [ H, H, H, H, ],
    ],
    "D": [
        [ H, H, H, _, ],
        [ H, _, _, H, ],
        [ H, _, _, H, ],
        [ H, _, _, H, ],
        [ H, H, H, _, ],
    ],
    "P": [
        [ H, H, H, _, ],
        [ H, _, _, H, ],
        [ H, H, H, _, ],
        [ H, _, _, _, ],
        [ H, _, _, _, ],
    ],
    "B": [
        [ H, H, H, _, ],
        [ H, _, _, H, ],
        [ H, H, H, _, ],
        [ H, _, _, H, ],
        [ H, H, H, _, ],
    ],
    "R": [
        [ H, H, H, _, ],
        [ H, _, _, H, ],
        [ H, H, H, _, ],
        [ H, _, _, H, ],
        [ H, _, _, H, ],
    ],
    "C": [
        [ _, H, H, ],
        [ H, _, _, ],
        [ H, _, _, ],
        [ H, _, _, ],
        [ _, H, H, ],
    ],
    "L": [
        [ H, _, _, ],
        [ H, _, _, ],
        [ H, _, _, ],
        [ H, _, _, ],
        [ H, H, H, ],
    ],
    ".": [
        [ _, _, ],
        [ _, _, ],
        [ _, _, ],
        [ _, _, ],
        [ H, _, ],
    ],
    "nul": [
        [ _, _, ],
        [ _, _, ],
        [ _, _, ],
        [ _, _, ],
        [ _, _, ],
    ],
}

palavras = dict(
    AMARELO="AM",
    VERDE="VD",
    AZUL="AZ",
    VERMELHO="VM",
    MARROM="MR",
    PRETO="PR",
    BRANCO="BR",
)

QTD_LINHAS = 5
def concatena_letras(*letras):
    ret = [[] for _ in range(QTD_LINHAS)]
    for i in range(QTD_LINHAS):
        for l in letras:
            ret[i] += l[i] + [_]
    return ret
        
def passo_anim(palavra, i):
    return [r[i:i+5] for r in palavra]

def mostrar_palavra(nome):
    mat = concatena_letras(*(letras.get(letra) or letras["nul"]
                             for letra in palavras.get(nome) or nome))
    for i in range(len(mat[0])):        
        m = passo_anim(mat, i)
        if len(m[0]) < QTD_LINHAS:
            m = [l + [_]*(QTD_LINHAS - len(l)) for l in m]

        yield globais.hub.display.icon(m)

def tela_escolher_cor(selecao, intervalo_anim=110, intervalo_botao=100):
    cor = Cor.enum(selecao)
    sw = StopWatch()

    for _ in mostrar_palavra(cor):
        sw.reset()
        globais.hub.light.on(cor2Color(selecao))
        while sw.time() < intervalo_anim:
            wait(intervalo_botao)
            botoes = globais.hub.buttons.pressed()
            if botoes: return botoes

    return {}
