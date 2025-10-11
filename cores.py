from pybricks.tools      import wait
from pybricks.parameters import Color

from lib.polyfill import Enum, rgb_to_hsv, hsv_to_rgb

from lib.cores_calibradas_ import mapa_hsv, mapa_hsv_frente

cor = Enum("cor", ["NENHUMA",
                   "PRETO",
                   "AZUL",
                   "VERDE",
                   "AMARELO",
                   "VERMELHO",
                   "BRANCO",
                   "MARROM"])

#! o mapa pro identificar deve tar errado pq a gente mudou a ordem do enum.
##! talvez tenha que mudar pra um dicionário

class Cor:
    enum = cor

    def __init__(self, color=None, hsv=None, cor=None):
        self.color = color or cor2Color(cor)
        self.cor   = cor   or Color2cor(color)
        self.hsv   = hsv   or Color2tuple(color)

        if self.hsv:
            self.h, self.s, self.v = self.hsv
        else:
            self.h, self.s, self.v = None, None, None

    def __iter__(self): # para poder fazer *Cor
        yield self.color
        yield self.hsv

    def __eq__(self, other): #! testar
        if isinstance(other, Color):
            if other == self.color: return True
        if isinstance(other, tuple):
            if other == self.hsv: return True
        if isinstance(other, int): #! enum cor
            if other == self.cor: return True
        #! retornar comparação direto?

        #! será que devia confiar no identificar?
        return ((other == self.color) or (other == self.hsv) or
                (identificar(other) == identificar(self.hsv)))

    def __str__(self):
        return f"{self.enum(self.cor)}[{self.h}, {self.s}, {self.v}]"

    def vermelho(self): return (self.color == Color.RED)
    def verde(self):    return (self.color == Color.GREEN)
    def branco(self):   return (self.color == Color.WHITE)
    def preto(self):    return (self.color == Color.PRETO)
    def azul(self):     return (self.color == Color.BLUE)

    def area_livre(self): return self.verde()
    def pista(self):      return self.branco() or self.verde()
    def parede(self):     return self.preto()
    def beco(self):       return self.vermelho()

def Color2tuple(color): #! falhar mais alto
    try:    return color.h, color.s, color.v
    except: return None #! except

def Color2cor(color): #! falhar mais alto
    res = {
        Color2tuple(Color.BLACK ): cor.PRETO,
        Color2tuple(Color.BLUE  ): cor.AZUL,
        Color2tuple(Color.GREEN ): cor.VERDE, 
        Color2tuple(Color.YELLOW): cor.AMARELO,
        Color2tuple(Color.RED   ): cor.VERMELHO,
        Color2tuple(Color.WHITE ): cor.BRANCO,
        Color2tuple(Color.BROWN ): cor.MARROM,
    }.get(Color2tuple(color))
    return res if res is not None else cor.NENHUMA

def cor2Color(cor): #! falhar mais alto
    res = {
        cor.NENHUMA:  Color.NONE,
        cor.PRETO:    Color.BLACK,
        cor.AZUL:     Color.BLUE,
        cor.VERDE:    Color.GREEN,
        cor.AMARELO:  Color.YELLOW,
        cor.VERMELHO: Color.RED,
        cor.BRANCO:   Color.WHITE,
        cor.MARROM:   Color.BROWN
    }.get(cor)
    return res


#hsv = tuple[float, float, float]

def norm_hsv(hsv):
    if type(hsv) != tuple:
        h, s, v = hsv.h, hsv.s, hsv.v
    else:
        h, s, v = hsv
    return (h/360, s/100, v/100)

def unnorm_hsv(hsv):
    h, s, v = hsv
    return (h*360, s*100, v*100)

def todas(sensor_esq, sensor_dir) -> tuple[tuple, tuple]:
    esq = Cor(sensor_esq.color(), sensor_esq.hsv())
    dir = Cor(sensor_dir.color(), sensor_dir.hsv())
    return (esq, dir)

def iter_coleta(hub, botao_parar, sensor):
    minm, maxm = (360, 100, 100), (0, 0, 0)
    soma, cont = (000, 000, 000), 0
    while botao_parar not in hub.buttons.pressed():
        hsv = sensor.hsv()
        hsv = hsv.h, hsv.s, hsv.v

        rgb_norm = hsv_to_rgb(norm_hsv(hsv))

        minm = tuple(map(min, minm, hsv))
        maxm = tuple(map(max, maxm, hsv))

        soma = tuple(map(lambda c,s: c+s, hsv, soma))
        cont += 1

        if 1:
            cor_txt_rgb = tuple(map("{:.2f}".format, rgb_norm))
            cor_txt_hsv = tuple(map("{:.2f}".format, hsv))
            print(cor_txt_hsv, cor_txt_rgb)

        yield (minm, soma, cont, maxm)


def coletar_valores(hub, botao_parar, esq=None, dir=None) -> tuple[hsv, hsv, hsv]: # type: ignore
    wait(200)
    if esq and dir:
        for info_esq, info_dir in zip(iter_coleta(hub, botao_parar, esq),
                                      iter_coleta(hub, botao_parar, dir)):
            minme, somae, conte, maxme = info_esq
            minmd, somad, contd, maxmd = info_dir

            minm = tuple(map(min, minme, minmd))
            soma = tuple(map(lambda c,s: c+s, somad, somae))
            cont = conte + contd
            maxm = tuple(map(max, maxme, maxmd))
            #! fiz assim provisoriamente, acho que devia ser separado por lado mesmo
    else:
        sensor = esq if esq else dir
        for info in iter_coleta(hub, botao_parar, sensor):
            minm, soma, cont, maxm = info

    med = tuple(map(lambda s: s/cont, soma))
    print("max:", maxm, "med:", med, "min:", minm)

    return (minm, tuple(map(round, med)), maxm)

def identificar_por_intervalo_hsv(hsv, mapa) -> cor: # type: ignore
    h, s, v = hsv
    
    if   v <= 20: #! usar valores do arquivo
        return cor.PRETO
    elif s <= 10 and v >= 90:
        return cor.BRANCO

    for i, (m, mm, M) in enumerate(mapa):
        hm, _, _ = m
        hM, _, _ = M

        if h in range(hm, hM): return i
    return cor.NENHUMA

def identificar_por_hue_medio(hsv, mapa) -> int:
    h, s, v = hsv
    menor_diferenca = float('inf')
    indice_mais_perto = None

    for i, (_, medM, _) in enumerate(mapa):
        # Considera apenas a componente media (hM)
        hm, _, _ = medM
        diferenca = abs(h - hm)  #  representa a média do hue
        if diferenca < menor_diferenca:
            indice_mais_perto = i
            menor_diferenca = diferenca
    
    if indice_mais_perto is None:
        return cor.NENHUMA  # Retorne um valor padrão se não encontrar nada

    return indice_mais_perto  # Retorna o índice da cor mais próxima


def identificar(color, sensor="chao") -> cor: # type: ignore   
    if sensor == "frente":
        identificar_cor = identificar_por_hue_medio
        mapa = mapa_hsv_frente
    elif sensor == "chao":
        identificar_cor = identificar_por_intervalo_hsv
        mapa = mapa_hsv

    try: #! ver jeito melhor
        return identificar_cor(color, mapa)
    except TypeError as e:
        print(f"cores.identificar: {e}")
        hsv = color.h, color.s, color.v
        return identificar_cor(hsv, mapa)


def certificar(sensor_dir, sensor_esq, uni, uni2=None) -> bool:
    if uni2 is None: uni2 = uni
    esq, dir = todas(sensor_esq, sensor_dir)

    res = uni(esq) and uni2(dir)
    print(f"certificar_cor: {res=}")

    return res


def repl_calibracao(mapa_hsv, lado=""):
    print(f"mapa_hsv{lado} = [")
    for c in range(len(cor)-1): # -1 pula cor NENHUMA
        print(f"\t{mapa_hsv[c]}, #{cor(c)}")
    print("]")
