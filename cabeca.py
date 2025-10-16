from pybricks.hubs import PrimeHub

from pybricks.pupdevices import Motor, ColorSensor, UltrasonicSensor
from pybricks.parameters import Port, Stop, Side, Axis, Direction, Button, Color

from pybricks.tools      import wait, StopWatch
from pybricks.robotics   import DriveBase

from lib.caminhos import achar_movimentos, achar_caminhos, tipo_movimento
from lib.caminhos import coloca_obstaculo, tira_obstaculo, pegar_celulas_incertas, imprimir_mapa

from urandom import choice

import bluetooth as blt
import gui
import cores

from cores import Cor

from comum import globais, bipes, luzes
from comum import LOG, ERRO, ASSERT


NUM_CUBOS_PEGÁVEIS = 2

VEL_ALINHAR = 80
VEL_ANG_ALINHAR = 20
GIRO_MAX_ALINHAR = 90 #70

TAM_QUARTEIRAO = 300
TAM_BLOCO = TAM_QUARTEIRAO//2
TAM_FAIXA = 20

NUM_CAÇAMBAS = 5
TAM_CAÇAMBA = 160
TAM_CUBO = 50

DIST_EIXO_SENSOR = 45
DIST_EIXO_SENSOR_FRENTE = 110
DIST_EIXO_SENSOR_TRAS = 110
DIST_CRUZAMENTO_CUBO = TAM_BLOCO - DIST_EIXO_SENSOR_FRENTE
DIST_EXTRA_CUBO = 0 #TAM_CUBO//2

DIST_BORDA_CAÇAMBA = 130
DIST_CAÇAMBA = 100
DIST_VERDE_CAÇAMBA = 80

PISTA_TODA = TAM_QUARTEIRAO*6
BLOCO_MEIO = 4

DISTS_CAÇAMBAS = [ DIST_BORDA_CAÇAMBA +
                   TAM_CAÇAMBA*i + DIST_CAÇAMBA*i
                   for i in range(NUM_CAÇAMBAS) ]
cubos_caçambas = [0 for i in range(NUM_CAÇAMBAS)]
cores_caçambas = []


#! 2024: checar stall: jogar exceção
#! 2024: checar cor errada no azul

#! a gente não leva em consideração a distância entre o sensor e a roda
##! na hora de começar a procura e não leva em consideração a distância
##! entre a roda e a garra na hora de pegar

#! a procura para no meio quando vê um cubo desconhecido e acha que é catástrofe

#! adicionar botão de "soft-reset", que faz o robô começar do início mas
##! ainda com o estado dele (caçambas etc)
##! fazer com bluetooth no braco pra ser mais fácil de apertar
##! quando sofrer exceção e DEBUG == False, entrar num estado que só espera isso


def setup():
    global hub, rodas
    global sensor_cor_esq, sensor_cor_centro, sensor_cor_dir
    global botao_calibrar, orientação_estimada
    global rodas_conf_padrao, vels_padrao, vel_padrao, vel_ang_padrao #! fazer um dicionário e concordar com mudar_velocidade

    hub = PrimeHub(broadcast_channel=blt.TX_CABECA,
                   observe_channels=[blt.TX_BRACO, blt.TX_RABO],
                   front_side=Axis.X, top_side=-Axis.Z)
    hub.system.set_stop_button(Button.CENTER)
    globais.init(hub, TESTE, DEBUG, nome="cabeça")

    orientação_estimada = ""

    sensor_cor_esq    = ColorSensor(Port.D)
    sensor_cor_centro = ColorSensor(Port.E)
    sensor_cor_dir    = ColorSensor(Port.C)

    roda_esq = Motor(Port.B, positive_direction=Direction.COUNTERCLOCKWISE)
    roda_dir = Motor(Port.A, positive_direction=Direction.CLOCKWISE)
    rodas    = DriveBase(roda_esq, roda_dir,
                         wheel_diameter=88,
                         axle_track=145.5) #! recalibrar
    rodas.use_gyro(True)

    botao_calibrar = Button.BLUETOOTH

    rodas_conf_padrao = rodas.settings() #! CONSTANTIZAR
    vel_padrao     = rodas_conf_padrao[0]
    vel_ang_padrao = rodas_conf_padrao[2]
    vels_padrao    = vel_padrao, vel_ang_padrao

    return hub

def main():
    global orientação_estimada, pos_estimada, cores_caçambas
    blt.SILENCIOSO = True

    blt.resetar_garra()
    blt.abaixar_garra()
    posicionamento_inicial()
    pos_estimada = (0,0)
    if not cores_caçambas:
        descobrir_cor_caçambas()
        acertar_orientação("L")
        achar_azul_alinhado()
        dar_re_alinhar_primeiro_bloco()

        if choice((True, False)):
            acertar_orientação("S")
            achar_nao_verde_alinhado()
            dar_re_alinhar_primeiro_bloco()
            acertar_orientação("L")
            pos_estimada = (8,0)
        else:
            posicionamento_inicial()

    while True:
        blt.resetar_garra()
        blt.abaixar_garra()
        posicionamento_inicial()
        pos_estimada = (0,0)

        achar_nao_verde_alinhado()
        dar_re(TAM_BLOCO//2)
        achar_nao_verde_alinhado()
        rodas.straight(DIST_EIXO_SENSOR)

        cor, pos_estimada = procura(pos_estimada, cores_caçambas)
        caminho_volta = achar_caminhos(pos_estimada, (0,0))
        seguir_caminho(caminho_volta)
        colocar_cubo_na_caçamba(cor)
        dar_re(DIST_VERDE_CAÇAMBA)

def test():
    global orientação_estimada, pos_estimada, cores_caçambas
    ... # testar coisas aqui sem mudar o resto do código

    while False:
        esq    = sensor_cor_esq.reflection()
        centro = sensor_cor_centro.reflection()
        dir    = sensor_cor_dir.reflection()
        print(esq, centro, dir)

    global mul_direção_seguir_linha
    while True:
        if False: vel = 70
        else:     vel, *_ = rodas.settings()

        for _ in range(5):
            #curva_linha_esquerda() #!??? tá trocado e acho que funcionou
            achar_cruzamento(vel)
            bipes.separador()
            mul_direção_seguir_linha = -1
            rodas.curve(DIST_EIXO_SENSOR, -90)

        #curva_linha_esquerda()
        achar_cruzamento(vel)
        bipes.separador()
        mul_direção_seguir_linha = +1
        rodas.curve(DIST_EIXO_SENSOR, -90)

        #curva_linha_direita()
        achar_cruzamento(vel)
        bipes.separador()
        mul_direção_seguir_linha = -1
        rodas.curve(DIST_EIXO_SENSOR, 90)


    while True:
        blt.abrir_garra()
        ang = blt.fechar_garra() #...
        print(ang)
    testes.imprimir_cor_cubo_para_sempre()

    if False:
        cores_caçambas = [
            Cor.enum.VERMELHO, Cor.enum.AMARELO, Cor.enum.AZUL, Cor.enum.VERDE, Cor.enum.PRETO
        ]
    if False: orientação_estimada = "N"
    if False: orientação_estimada = "S"
    if False: orientação_estimada = "L"
    if False: orientação_estimada = "O"

    main()


class mudar_velocidade():
    """
    gerenciador de contexto (bloco with) para (automaticamente):
    1. mudar a velocidade do robô
    2. restaurar a velocidade do robô
    """
    def __init__(self, vel, vel_ang=None, drive_base=None): 
        self.rodas = drive_base or rodas
        self.vel   = vel
        self.vel_ang = vel_ang
 
    def __enter__(self): 
        self.conf_anterior = self.rodas.settings()
        [_, *conf_resto]   = self.conf_anterior
        if self.vel_ang:
            conf_resto[1] = self.vel_ang
        self.rodas.settings(self.vel, *conf_resto)
        return self

    def __exit__(self, exc_type, exc_value, exc_traceback): 
        self.rodas.settings(*self.conf_anterior)

def inverte_orientação(ori=None):
    if ori == None: ori = orientação_estimada

    if ori == "N": return "S"
    if ori == "S": return "N"
    if ori == "L": return "O"
    if ori == "O": return "L"

    return ori #!< não é pra chegar aqui

def dar_meia_volta():
    global orientação_estimada
    rodas.turn(180)

    orientação_estimada = inverte_orientação()
    LOG(f"dar_meia_volta: {orientação_estimada=}")

def virar_direita():
    global orientação_estimada
    rodas.turn(90)

    if   orientação_estimada == "N": orientação_estimada = "L"
    elif orientação_estimada == "S": orientação_estimada = "O"
    elif orientação_estimada == "L": orientação_estimada = "S"
    elif orientação_estimada == "O": orientação_estimada = "N"
    LOG(f"virar_direita: {orientação_estimada=}")

def virar_esquerda():
    global orientação_estimada
    rodas.turn(-90)

    if   orientação_estimada == "N": orientação_estimada = "O"
    elif orientação_estimada == "S": orientação_estimada = "L"
    elif orientação_estimada == "L": orientação_estimada = "N"
    elif orientação_estimada == "O": orientação_estimada = "S"
    LOG(f"virar_esquerda: {orientação_estimada=}")

DIST_PARAR=0.4 #! checar valor
def parar():
    rodas.straight(-DIST_PARAR)
    rodas.stop()
ANG_PARAR=0.0
def parar_girar():
    rodas.turn(-ANG_PARAR)
    rodas.stop()

def dar_re(dist):
    rodas.straight(-dist)

def dar_re_alinhar_primeiro_bloco():
    dar_re(TAM_BLOCO - DIST_EIXO_SENSOR - TAM_FAIXA//2)
    LOG("dar_re_meio_quarteirão: ré")

def dar_re_meio_quarteirao():
    dar_re(TAM_BLOCO - DIST_EIXO_SENSOR)
    LOG("dar_re_meio_quarteirão: ré")

#! provavelmente mudar andar_ate pra receber uma fn -> bool e retornar só bool, dist (pegar as informações extras na própria função)

def ver_nao_pista() -> tuple[bool, tuple[Color, hsv], tuple[Color, hsv]]: # type: ignore
    esq, dir = cores.todas(sensor_cor_esq, sensor_cor_dir)
    return ((not esq.pista() or not dir.pista()), esq, dir)

def ver_nao_verde() -> tuple[bool, tuple[Color, hsv], tuple[Color, hsv]]: # type: ignore
    esq, dir = cores.todas(sensor_cor_esq, sensor_cor_dir)
    if not esq.verde() or not dir.verde(): LOG(f"ver_não_verde: {esq}, {dir}")
    return ((not esq.area_livre() or not dir.area_livre()), esq, dir)

def verificar_cor(func_cor) -> Callable[None, tuple[bool, int]]: # type: ignore
    def f():
        esq, dir = cores.todas(sensor_cor_esq, sensor_cor_dir)
        return (func_cor(esq) or func_cor(dir), esq, dir)
    return f


def ver_cubo_perto() -> bool:
    cor = blt.ver_cor_cubo()
    return cor != Cor.enum.NENHUMA

def andar_ate_idx(*conds_parada: Callable, dist_max=PISTA_TODA) -> tuple[bool, tuple[Any]]: # type: ignore
    rodas.reset()
    rodas.straight(dist_max, wait=False)
    while not rodas.done():
        for i, cond_parada in enumerate(conds_parada):
            chegou, *retorno = cond_parada()
            if not chegou: continue
            else:
                parar()
                return i+1, retorno
    return 0, (rodas.distance(),)

nunca_parar   = (lambda: (False, False))
ou_manter_res = (lambda res, ext: (res, ext))

def andar_ate_bool(sucesso, neutro=nunca_parar, fracasso=ver_nao_pista,
                            ou=ou_manter_res, dist_max=PISTA_TODA):
    succ, neut, frac = 1, 2, 3
    while True:
        res, extra = andar_ate_idx(sucesso, neutro, fracasso,
                                   dist_max=dist_max)

        if   res == succ: return True, extra
        elif res == frac: return False, extra
        elif res == neut: continue
        elif res == 0:
            LOG("andar_ate_bool: andou demais")
            return False, (None,) #ou(res, extra)
        else: 
            LOG(f"andar_ate_bool: {res}")
            assert False

def cor_final(retorno):
    achou, extra = retorno

    if achou: return extra
    else:     return cores.todas(sensor_cor_esq, sensor_cor_dir)

def achar_limite() -> tuple[tuple[Color, hsv], tuple[Color, hsv]]: # type: ignore
    return cor_final(andar_ate_idx(ver_nao_pista))

def achar_nao_verde() -> tuple[tuple[Color, hsv], tuple[Color, hsv]]:
    return cor_final(andar_ate_idx(ver_nao_verde))

def achar_azul() -> tuple[tuple[Color, hsv], tuple[Color, hsv]]:
    return cor_final(andar_ate_idx(verificar_cor(Cor.azul)))

def achar_azul_alinhado():
    achar_azul()
    dar_re(TAM_FAIXA) #!//2?
    return alinhar()#alinha_giro() #

def achar_nao_verde_alinhado():
    achar_nao_verde()
    dar_re(TAM_FAIXA) #!//2?
    return alinhar()#alinha_giro() #

mul_direção_seguir_linha = 1
def achar_cruzamento(vel):
    REFL_MAX = 99
    REFL_MIN = 13
    REFL_IDEAL = (REFL_MAX + REFL_MIN)/2

    def preto(val):
        return val <= REFL_MIN + 5

    kp = .50
    while True:
        esq    = sensor_cor_esq.reflection()
        centro = sensor_cor_centro.reflection()
        dir    = sensor_cor_dir.reflection()

        erro = REFL_IDEAL - centro
        ang  = mul_direção_seguir_linha*(erro*kp)
        rodas.drive(vel, ang)

        if preto(esq) and preto(dir): break

    rodas.stop()


def alinha_parede(vel, vel_ang, giro_max=45,
                  func_cor_pista=Cor.area_livre,
                  func_parar_andar=ver_nao_verde
                  ) -> bool:
    desalinhado_branco = lambda esq, dir: Cor.branco(esq) ^ Cor.branco(dir)
    alinhado_nao_pista = lambda esq, dir: ((not func_cor_pista(esq)) and
                                           (not func_cor_pista(dir)))
    
    alinhado_pista  = lambda esq, dir: func_cor_pista(esq) and func_cor_pista(dir)
    alinhado_parede = lambda esq, dir: alinhado_nao_pista(esq, dir) and not desalinhado_branco(esq, dir)

    with mudar_velocidade(vel, vel_ang):
        parou, extra = andar_ate_idx(func_parar_andar, dist_max=TAM_BLOCO)
        if not parou:
            (dist,) = extra
            LOG(f"alinha_parede: reto pista {dist}")
            return False, extra # viu só branco, não sabemos se tá alinhado
    
        (esq, dir) = extra
        if  alinhado_parede(esq, dir):
            LOG(f"alinha_parede: reto não pista {esq}, {dir}")
            return True, extra
        elif not func_cor_pista(dir):
            LOG(f"alinha_parede: torto pra direita {esq}, {dir}")
            GIRO = giro_max
        elif not func_cor_pista(esq):
            LOG(f"alinha_parede: torto pra esquerda {esq}, {dir}")
            GIRO = -giro_max

        rodas.turn(GIRO, wait=False) #! fazer gira_ate
        LOG("alinha_parede: girando")
        while not rodas.done():
            extra = cores.todas(sensor_cor_esq, sensor_cor_dir)
            esq, dir = extra
            if  alinhado_parede(esq, dir):
                LOG(f"alinha_parede: alinhado parede: {esq}, {dir}")
                parar_girar()
                return True, extra # deve tar alinhado
            elif alinhado_pista(esq, dir):
                LOG(f"alinha_parede: alinhado pista: {esq}, {dir}")
                parar_girar()
                return False, extra #provv alinhado, talvez tentar de novo
        LOG(f"alinha_parede: girou tudo, {esq}, {dir}")
        return False, extra # girou tudo, não sabemos se tá alinhado

def alinha_giro(max_tentativas=4, virar=True, #! virar=False?
                              vel=VEL_ALINHAR, vel_ang=VEL_ANG_ALINHAR,
                              giro_max=GIRO_MAX_ALINHAR) -> None:
    for _ in range(max_tentativas): #! esqueci mas tem alguma coisa
        rodas.reset()
        alinhou, extra = alinha_parede(vel, vel_ang, giro_max=giro_max)

        ang  = rodas.angle()
        dist = rodas.distance()
        with mudar_velocidade(vel, vel_ang):
            rodas.turn(-ang)
            dar_re(dist)
            rodas.turn(ang)

        if alinhou: return extra
        else:
            if virar: virar_direita() #! testar agora
            continue
    return extra

def alinhar(max_tentativas=4, virar=True, #! virar=False?
                              vel=VEL_ALINHAR, vel_ang=VEL_ANG_ALINHAR,
                              giro_max=GIRO_MAX_ALINHAR) -> None:
    for _ in range(max_tentativas):
        rodas.reset()

        alinhou, extra = alinha_parede(vel, vel_ang, giro_max=giro_max)
        ang  = rodas.angle()
        dist = rodas.distance()
        if alinhou: return extra
        else:
            with mudar_velocidade(80, 30):
                rodas.turn(-ang)
                dar_re(dist)
                rodas.turn(ang)
    #! às vezes ele retorna como verde verde, tentei fazer isso pra resolver
    #if extra == (Cor.enum.VERDE, Cor.enum.VERDE):
    #    LOG("alinhar: vou na fé")
    #    return achar_nao_verde()
    return extra

def alinha_re(max_tentativas=3,
              vel=VEL_ALINHAR, vel_ang=VEL_ANG_ALINHAR,
              giro_max=70) -> None:
    for _ in range(max_tentativas):
        rodas.reset()
        dar_re_meio_quarteirao()

        alinhou, extra = alinha_parede(vel, vel_ang, giro_max=giro_max)
        ang  = rodas.angle()
        dist = rodas.distance()
        if alinhou: return
        else:
            with mudar_velocidade(80, 30):
                rodas.turn(-ang)
                dar_re(dist)
                rodas.turn(ang)
    return extra

def seguir_caminho(caminho): #! lidar com outras coisas
    def interpretar_movimento(mov):
        #! fazer run length encoding aqui
        if   mov == tipo_movimento.FRENTE:
            rodas.straight(TAM_BLOCO, then=Stop.COAST)
        elif mov == tipo_movimento.TRAS:
            dar_meia_volta()
            rodas.straight(TAM_BLOCO, then=Stop.COAST)
        elif mov == tipo_movimento.ESQUERDA_FRENTE:
            virar_esquerda()
            rodas.straight(TAM_BLOCO, then=Stop.COAST)
        elif mov == tipo_movimento.DIREITA_FRENTE:
            virar_direita()
            rodas.straight(TAM_BLOCO, then=Stop.COAST)
        elif mov == tipo_movimento.ESQUERDA:
            virar_esquerda()
        elif mov == tipo_movimento.DIREITA:
            virar_direita()

    def interpretar_caminho(caminho): #! receber orientação?
        for mov in caminho: #! yield orientação nova?
            LOG(f"seguir_caminho: {tipo_movimento(mov)}")
            interpretar_movimento(mov)
            yield rodas.distance()

    movs, ori_final = achar_movimentos(caminho, orientação_estimada)
    #LOG(*(tipo_movimento(mov) for mov in movs))

    for _ in interpretar_caminho(movs):
        while not rodas.done(): pass

    acertar_orientação(ori_final)

def acertar_orientação(ori):
    if True:
        cardinais = ["N", "L", "S", "O"]
        idx_ori_final = cardinais.index(ori)
        idx_ori_atual = cardinais.index(orientação_estimada)

        idx_diff = ((idx_ori_atual - idx_ori_final) % len(cardinais)) - 2
        if idx_diff == -2: return
        if idx_diff == -1: virar_esquerda()
        if idx_diff ==  0: dar_meia_volta()
        if idx_diff ==  1: virar_direita()
    else:
        while orientação_estimada != ori:
            LOG(f"{orientação_estimada=}, {ori=}")
            virar_direita()

def posicionamento_inicial():
    global orientação_estimada

    viu_vermelho = False
    while not (viu_vermelho and orientação_estimada == "L"):
        esq, dir = achar_nao_verde_alinhado()

        bipes.separador()
        dar_re_meio_quarteirao()
        if   esq.azul() or dir.azul():
            ASSERT(esq.azul() and dir.azul(), f"pos_ini: {esq} == {dir}")
            orientação_estimada = "L"
            virar_esquerda()
        elif esq.beco() or dir.beco():
            ASSERT(esq.beco() and dir.beco(), f"pos_ini: {esq} == {dir}")
            viu_vermelho = True
            virar_direita()
        else:
            ASSERT(esq.amarelo() or dir.amarelo(), f"pos_ini: {esq} e {dir} assumidos amarelo")
            orientação_estimada = "O"
            virar_direita()

#começar da linha ate dist caçamba i - dist traseira ate sensor
def alinhar_caçambas(): 
    """
    vai até amarelo
    aí vira e vai reto até o vermelho,
    depois vira pro lado contrário (direção das caçambas)
    """
    acertar_orientação("O")
    ASSERT(orientação_estimada == "O", "alinhar_caçambas: é pra ser oeste!")

    achar_nao_verde_alinhado()
    LOG("alinhar_caçambas: viu não verde (espera amarelo)")
    dar_re_meio_quarteirao()

    virar_direita()
    achar_nao_verde_alinhado()
    LOG("alinhar_caçambas: viu não verde (espera vermelho)")

    dar_re(DIST_BORDA_CAÇAMBA + DIST_EIXO_SENSOR)
    dar_meia_volta()

def colocar_cubo_na_caçamba(cor_cubo, max_cubos=NUM_CUBOS_PEGÁVEIS): #! suportar 3 cubos rs
    global cubos_caçambas
    margem      = TAM_CUBO//2 if max_cubos != 1 else (TAM_CUBO*3)//2
    espaçamento = TAM_CUBO    if max_cubos == 2 else 0

    ASSERT(cor_cubo != Cor.enum.NENHUMA)
    blt.levantar_garra()
    alinhar_caçambas()
    for i, (cor, dist) in enumerate(zip(cores_caçambas, DISTS_CAÇAMBAS)):
        if cor_cubo == cor:
            if cubos_caçambas[i] > max_cubos: continue

            rodas.straight(dist - DIST_BORDA_CAÇAMBA - margem
                          + cubos_caçambas[i]*(TAM_CUBO + espaçamento))
            blt.abaixar_garra()
            blt.levantar_garra()
            virar_direita()

            achar_nao_verde_alinhado()
            rodas.straight(DIST_VERDE_CAÇAMBA-20)
            blt.abrir_garra()

            cubos_caçambas[i] += 1
            return

    raise SucessoOuCatástrofe("sem lugar pro cubo nas caçambas")

#! considerar adversário
def procura_inicial(xy, caçambas):
    entra_primeira_rua()

    x, _ = xy #! para procura genérico, usar y também
    i, extra = andar_ate_idx(ver_cubo_perto, ver_nao_pista)
    while i == 2:
        x += 2 #! para procura genérico, considerar orientação
        i, extra = andar_ate_idx(ver_cubo_perto, ver_nao_pista)
    ASSERT(i == 1, "procura inicial: deveria ser impossível andar demais")

    cor = extra
    if cor in caçambas:
        pegar_cubo()
        dar_re_até_verde(xy)
        #! fazer_caminho_contrário() #! voltar_para_verde(xy)
        return cor, xy
    else:
        fazer_caminho_contrário() #! voltar_para_verde(xy)
        xy = andar_1_quarteirão_no_eixo_y(xy)
        return procura_inicial(xy, caçambas)

def partial(func, *args, **kwargs):
    return lambda *a, **kw: func(*args, *a, **kwargs, **kw)

#! tá empurrando?
def procura(pos_estimada, cores_caçambas):
    cel_incertas = pegar_celulas_incertas()
    cel_atual = pos_estimada

    caminhos_incertas = {
        cel: achar_caminhos(cel_atual, cel) for cel in cel_incertas
    }
    cel_incertas.sort(key=lambda x: (
        len(caminhos_incertas[x]) if caminhos_incertas[x] is not None else 9000
    ))

    blt.resetar_garra()
    blt.abaixar_garra()
    for cel_destino in cel_incertas:
        LOG("tentando de", cel_atual, "até :", cel_destino)

        caminho = achar_caminhos(cel_atual, cel_destino)
        if not caminho:
            LOG("procura: nenhum caminho encontrado")
            continue

        # anda até ficar imediatamente antes da celula destino
        caminho.pop(-1)
        seguir_caminho(caminho)
        cel_atual = caminho[-1]

        # acerta orientação para como se tivesse andado tudo
        restante = [cel_atual, cel_destino]
        _, ori_final = achar_movimentos(restante, orientação_estimada)
        acertar_orientação(ori_final)

        # vê se tem alguma coisa na frente
        rodas.straight(DIST_CRUZAMENTO_CUBO + DIST_EXTRA_CUBO, then=Stop.COAST)
        ang = blt.fechar_garra()
        if ang > 145:
            LOG("procura: cel livre fechou tudo")
            tira_obstaculo(cel_destino)
            rodas.straight(TAM_BLOCO - DIST_CRUZAMENTO_CUBO - DIST_EXTRA_CUBO, then=Stop.COAST)
            cel_atual = cel_destino
            blt.abrir_garra()
            continue

        cor = blt.ver_cor_cubo()
        luzes.mostrar(cor.color) #! fzr printar em braco
        if cor == Cor.enum.BRANCO:
            bipes.cabeca()
        if cor == Cor.enum.NENHUMA:
            LOG("procura: cel livre viu NENHUM")
            tira_obstaculo(cel_destino)
            rodas.straight(TAM_BLOCO - DIST_CRUZAMENTO_CUBO - DIST_EXTRA_CUBO, then=Stop.COAST)
            cel_atual = cel_destino
            continue
        if ((cor not in cores_caçambas) or
            (cubos_caçambas[cores_caçambas.index(cor)] >= NUM_CUBOS_PEGÁVEIS)):
            LOG(f"procura: cubo desconhecido cor {cor}")
            coloca_obstaculo(cel_destino)
            dar_re(DIST_EXTRA_CUBO)
            blt.abrir_garra()
            dar_re(DIST_CRUZAMENTO_CUBO)
            continue

        imprimir_mapa()

        LOG(f"procura: cubo cor {cor}")
        tira_obstaculo(cel_destino)
        dar_re(DIST_CRUZAMENTO_CUBO + DIST_EXTRA_CUBO)
        return cor, cel_atual

    imprimir_mapa()

    raise SucessoOuCatástrofe()

def descobrir_cor_caçambas():
    global cores_caçambas
    if not cores_caçambas:
        cores_caçambas = [Cor(cor=Cor.enum.NENHUMA) for i in range(NUM_CAÇAMBAS)]

    alinhar_caçambas()
    rodas.straight(DIST_EIXO_SENSOR_TRAS-10)
    virar_direita()

    achar_nao_verde_alinhado()
    rodas.straight(DIST_VERDE_CAÇAMBA-41) #! tá muito longe! era 45 testar 43
    virar_esquerda()
    for i in range(NUM_CAÇAMBAS):
        cores_caçambas[i] = blt.ver_cor_caçamba()
        dist = blt.ver_dist_caçamba()

        if cores_caçambas[i].cor == Cor.enum.MARROM:
            cores_caçambas[i] = Cor(cor=Cor.enum.AMARELO)
        if cores_caçambas[i].cor == Cor.enum.PRETO:
            if True: cores_caçambas[i] = Cor(cor=Cor.enum.AZUL)
            else:    cores_caçambas[i] = Cor(cor=Cor.enum.VERDE)
        if cores_caçambas[i].cor == Cor.enum.NENHUMA:
            if (dist < TAM_QUARTEIRAO):
                cores_caçambas[i] = Cor(cor=Cor.enum.PRETO)

        LOG(f"descobrir_cor_caçamba: caçamba {cores_caçambas[i]} a {dist/10}cm")

        if i+1 < NUM_CAÇAMBAS:
            rodas.straight(TAM_CAÇAMBA+DIST_CAÇAMBA)
    LOG(f"descobrir_cor_caçamba: cores_caçambas = {cores_caçambas}")


class testes:
    @staticmethod
    def imprimir_cor_caçamba_para_sempre():
        while True:
            cor = blt.ver_cor_caçamba()
            print(cor)

    @staticmethod
    def imprimir_dist_caçamba_pra_sempre():
        while True:
            dist = blt.ver_dist_caçamba()
            print(f"{dist=}")

    @staticmethod
    def imprimir_cor_cubo_para_sempre():
        blt.SILENCIOSO = True
        while True:
            hsv = None #blt.ver_hsv_cubo()
            cor = blt.ver_cor_cubo()
            print(f"hsv: {hsv}, cor: {cor}")

    @staticmethod
    def imprimir_caçamba_para_sempre():
        blt.SILENCIOSO = True
        while True:
            dist = blt.ver_dist_caçamba()
            cor  = blt.ver_cor_caçamba()
            print(f"dist: {dist}, cor: {cor}")

if __name__ == "__main__":
    try:    TESTE == True
    except: TESTE = False
    try:    DEBUG == True
    except: DEBUG = False

    hub = setup()
    try:
        bipes.inicio()
        if TESTE: test()
        else:     main()
        bipes.final()
    except Exception as e:
        bipes.falha()
        raise e
