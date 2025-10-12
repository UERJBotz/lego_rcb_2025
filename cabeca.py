from pybricks.hubs import PrimeHub

from pybricks.pupdevices import Motor, ColorSensor, UltrasonicSensor
from pybricks.parameters import Port, Stop, Side, Axis, Direction, Button, Color

from pybricks.tools      import wait, StopWatch
from pybricks.robotics   import DriveBase

from lib.bipes    import bipe_calibracao, bipe_cabeca, bipe_separador, musica_vitoria, musica_derrota

from lib.caminhos import achar_movimentos, achar_caminhos, tipo_movimento
from lib.caminhos import coloca_obstaculo, tira_obstaculo, pegar_celulas_incertas, imprimir_mapa

from urandom import choice

import bluetooth as blt
import gui
import cores

from cores import Cor

VEL_ALINHAR = 80
VEL_ANG_ALINHAR = 20
GIRO_MAX_ALINHAR = 90 #70

TAM_QUARTEIRAO = 300
TAM_BLOCO = TAM_QUARTEIRAO//2
TAM_FAIXA = 20

DIST_EIXO_SENSOR = 45
DIST_EIXO_SENSOR_FRENTE = 110
DIST_EIXO_SENSOR_TRAS = 110
DIST_CRUZAMENTO_CUBO = TAM_BLOCO - DIST_EIXO_SENSOR_FRENTE

NUM_CAÇAMBAS = 5
TAM_CAÇAMBA = 160
TAM_CUBO = 50

DIST_BORDA_CAÇAMBA = 130
DIST_CAÇAMBA = 100
DIST_VERDE_CAÇAMBA = 60 #73

PISTA_TODA = TAM_QUARTEIRAO*6

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
    global sensor_cor_esq, sensor_cor_dir, sensor_ultra_esq, sensor_ultra_dir
    global botao_calibrar, orientacao_estimada
    global rodas_conf_padrao, vels_padrao, vel_padrao, vel_ang_padrao #! fazer um dicionário e concordar com mudar_velocidade

    hub = PrimeHub(broadcast_channel=blt.TX_CABECA,
                   observe_channels=[blt.TX_BRACO,
                                     blt.TX_RABO],
                    front_side=Axis.X, top_side=-Axis.Z)
    nome, bat = hub.system.name(), hub.battery.voltage()

    print(f"{nome}: {bat}mV")
    while nome != "spike1":
        hub.speaker.beep(frequency=1024); wait(200)
    else:
        hub.light.blink(Color.RED, [100,50,200,100])
    blt.init(hub)

    hub.display.orientation(Side.BOTTOM) #!
    hub.system.set_stop_button(Button.CENTER)

    orientacao_estimada = ""

    sensor_cor_esq = ColorSensor(Port.D)
    sensor_cor_dir = ColorSensor(Port.C)

    roda_esq = Motor(Port.B, positive_direction=Direction.COUNTERCLOCKWISE)
    roda_dir = Motor(Port.A, positive_direction=Direction.CLOCKWISE)

    rodas = DriveBase(roda_esq, roda_dir,
                      wheel_diameter=88, axle_track=145.5) #! recalibrar
    #rodas.use_gyro(True)

    botao_calibrar = Button.BLUETOOTH

    rodas_conf_padrao = rodas.settings() #! CONSTANTIZAR
    vel_padrao     = rodas_conf_padrao[0]
    vel_ang_padrao = rodas_conf_padrao[2]
    vels_padrao = vel_padrao, vel_ang_padrao

    return hub

def main(hub):
    global orientacao_estimada, pos_estimada
    if deve_calibrar():
        mapa_hsv = menu_calibracao(hub,
                                   sensor_cor_esq,
                                   sensor_cor_dir)
        cores.repl_calibracao(mapa_hsv)#, lado="esq")

    blt.resetar_garra(hub)

    blt.abaixar_garra(hub)
    posicionamento_inicial(hub)

    if not cores_caçambas:
        descobrir_cor_caçambas()
    pos_estimada = (0,0)

    achar_nao_verde_alinhado()
    rodas.straight(DIST_EIXO_SENSOR)
    cor, pos_estimada = procura(hub, pos_estimada, cores_caçambas)
    caminho_volta = achar_caminhos(pos_estimada, (0,0))
    seguir_caminho(caminho_volta)
    colocar_cubo_na_caçamba(cor)

def test(hub):
    ... # testar coisas aqui sem mudar o resto do código
    global orientacao_estimada, pos_estimada, cores_caçambas
    #cores_caçambas = [Cor.enum.VERMELHO, Cor.enum.AMARELO, Cor.enum.AZUL, Cor.enum.VERDE, Cor.enum.PRETO]
    orientacao_estimada = "O"
    descobrir_cor_caçambas()
    return
    main(hub)


def LOG(*args, print=print, **kwargs):
    print("cabeça:", *args, **kwargs)

def ERRO(*args, bipar=True):
    from lib.bipes import bipe_falha
    LOG("ERRO:", *args); bipe_falha(hub)

def ASSERT(cond, texto=None):
    if DEBUG: assert cond, texto
    elif not cond:
        ERRO(f"assert '{texto}' falhou", bipar=DEBUG)
    return cond


class mudar_velocidade():
    """
    gerenciador de contexto (bloco with) para (automaticamente):
    1. mudar a velocidade do robô
    2. restaurar a velocidade do robô
    """
    def __init__(self, rodas, vel, vel_ang=None): 
        self.rodas = rodas
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

def inverte_orientacao(ori=None):
    if ori == None: ori = orientacao_estimada

    if ori == "N": return "S"
    if ori == "S": return "N"
    if ori == "L": return "O"
    if ori == "O": return "L"

    return ori #!< não é pra chegar aqui

def dar_meia_volta():
    global orientacao_estimada
    rodas.turn(180)

    orientacao_estimada = inverte_orientacao()
    LOG(f"dar_meia_volta: {orientacao_estimada=}")
    
def virar_direita():
    global orientacao_estimada
    rodas.turn(90)

    if   orientacao_estimada == "N": orientacao_estimada = "L"
    elif orientacao_estimada == "S": orientacao_estimada = "O"
    elif orientacao_estimada == "L": orientacao_estimada = "S"
    elif orientacao_estimada == "O": orientacao_estimada = "N"
    LOG(f"virar_direita: {orientacao_estimada=}")

def virar_esquerda():
    global orientacao_estimada
    rodas.turn(-90)

    if   orientacao_estimada == "N": orientacao_estimada = "O"
    elif orientacao_estimada == "S": orientacao_estimada = "L"
    elif orientacao_estimada == "L": orientacao_estimada = "N"
    elif orientacao_estimada == "O": orientacao_estimada = "S"
    LOG(f"virar_esquerda: {orientacao_estimada=}")

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

def dar_re_meio_quarteirao():
    dar_re(TAM_BLOCO - DIST_EIXO_SENSOR)
    LOG("dar_re_meio_quarteirão: ré")

#! provavelmente mudar andar_ate pra receber uma fn -> bool e retornar só bool, dist (pegar as informações extras na própria função)

def ver_nao_pista() -> tuple[bool, tuple[Color, hsv], tuple[Color, hsv]]: # type: ignore
    esq, dir = cores.todas(sensor_cor_esq, sensor_cor_dir)
    return ((not esq.pista() or not dir.pista()), esq, dir)

def ver_nao_verde() -> tuple[bool, tuple[Color, hsv], tuple[Color, hsv]]: # type: ignore
    esq, dir = cores.todas(sensor_cor_esq, sensor_cor_dir)
    LOG(f"ver_não_verde: {esq}, {dir}")
    return ((not esq.area_livre() or not dir.area_livre()), esq, dir)

def verificar_cor(func_cor) -> Callable[None, tuple[bool, int]]: # type: ignore
    def f():
        esq, dir = cores.todas(sensor_cor_esq, sensor_cor_dir)
        return (func_cor(*esq) or func_cor(*dir), esq, dir)
    return f


def ver_cubo_perto() -> bool:
    cor = blt.ver_cor_cubo(hub)
    return cor != cores.NENHUMA

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

def achar_nao_verde_alinhado():
    achar_nao_verde()
    dar_re(TAM_FAIXA) #!//2?
    return alinhar()#alinha_giro() #


def alinha_parede(vel, vel_ang, giro_max=45,
                  func_cor_pista=Cor.area_livre,
                  func_parar_andar=ver_nao_verde
                  ) -> bool:
    desalinhado_branco = lambda esq, dir: Cor.branco(esq) ^ Cor.branco(dir)
    alinhado_nao_pista = lambda esq, dir: ((not func_cor_pista(esq)) and
                                           (not func_cor_pista(dir)))
    
    alinhado_pista  = lambda esq, dir: func_cor_pista(esq) and func_cor_pista(dir)
    alinhado_parede = lambda esq, dir: alinhado_nao_pista(esq, dir) and not desalinhado_branco(esq, dir)

    with mudar_velocidade(rodas, vel, vel_ang):
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
        with mudar_velocidade(rodas, vel, vel_ang):
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
            with mudar_velocidade(rodas, 80, 30):
                rodas.turn(-ang)
                dar_re(dist)
                rodas.turn(ang)
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
            with mudar_velocidade(rodas, 80, 30):
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

    movs, ori_final = achar_movimentos(caminho, orientacao_estimada)
    #LOG(*(tipo_movimento(mov) for mov in movs))

    for _ in interpretar_caminho(movs):
        while not rodas.done(): pass

    acertar_orientacao(ori_final)

def acertar_orientacao(ori):
    while orientacao_estimada != ori:
        LOG(f"{orientacao_estimada=}, {ori=}")
        virar_direita()

def deve_calibrar():
    #! levar os dois sensores em consideração separadamente
    crono = StopWatch()
    while crono.time() < 100:
        botões = hub.buttons.pressed()
        if botao_calibrar in botões: return True
    return False

#! como dito em cores, isso deve tar quebrado por conta da ordem do enum
def menu_calibracao(hub, sensor_esq, sensor_dir,
                         botao_parar=Button.BLUETOOTH,
                         botao_aceitar=Button.CENTER,
                         botao_anterior=Button.LEFT,
                         botao_proximo=Button.RIGHT):
    hub.system.set_stop_button(
        (Button.CENTER, Button.BLUETOOTH)
    )
    bipe_calibracao(hub)
    mapa_hsv = cores.mapa_hsv.copy()

    selecao = 0

    wait(150)
    while True:
        botões = gui.tela_escolher_cor(hub, Cor.enum, selecao)

        if   botao_proximo  in botões:
            selecao = (selecao + 1) % len(Cor.enum)
            wait(100)
        elif botao_anterior in botões:
            selecao = (selecao - 1) % len(Cor.enum)
            wait(100)

        elif botao_aceitar in botões:
            [wait(100) for _ in gui.mostrar_palavra(hub, "CAL..")]
            mapa_hsv[selecao] = (
                cores.coletar_valores(hub, botao_aceitar, dir=sensor_dir, esq=sensor_esq)
            )
            wait(150)
        elif botao_parar   in botões:
            wait(100)
            break

    hub.system.set_stop_button(Button.CENTER)
    return mapa_hsv

def posicionamento_inicial(hub):
    global orientacao_estimada

    viu_vermelho = False
    while not (viu_vermelho and orientacao_estimada == "L"):
        esq, dir = achar_nao_verde_alinhado()

        bipe_separador(hub)
        dar_re_meio_quarteirao()
        if   esq.azul() and dir.azul():
            orientacao_estimada = "L"
            virar_esquerda()
        elif esq.beco() and dir.beco():
            viu_vermelho = True
            virar_direita()
        else: # amarelo assumido
            orientacao_estimada = "O"
            virar_direita()

#! considerar inimigo
def procura_inicial(hub, xy, caçambas):
    entra_primeira_rua(hub)

    x, _ = xy #! para procura genérico, usar y também
    i, extra = andar_ate_idx(ver_cubo_perto, ver_nao_pista)
    while i == 2:
        x += 2 #! para procura genérico, considerar orientação
        i, extra = andar_ate_idx(ver_cubo_perto, ver_nao_pista)
    ASSERT(i == 1, "procura inicial: deveria ser impossível andar demais")

    cor = extra
    if cor in caçambas:
        pegar_cubo(hub)
        dar_re_até_verde(hub, xy)
        #! fazer_caminho_contrário(hub) #! voltar_para_verde(hub, xy)
        return cor, xy
    else:
        fazer_caminho_contrário(hub) #! voltar_para_verde(hub, xy)
        xy = andar_1_quarteirão_no_eixo_y(hub, xy)
        return procura_inicial(hub, xy, caçambas)

#começar da linha ate dist caçamba i - dist traseira ate sensor
def alinhar_caçambas(): 
    """
    vai até amarelo
    aí vira e vai reto até o vermelho,
    depois vira pro lado contrário (direção das caçambas)
    """
    if (orientacao_estimada == "L"): dar_meia_volta()
    if (orientacao_estimada == "S"): virar_direita()
    if (orientacao_estimada == "N"): virar_esquerda()
    ASSERT(orientacao_estimada == "O", "alinhar_caçambas: é pra ser oeste!")

    achar_nao_verde_alinhado()
    LOG("alinhar_caçambas: viu não verde (espera amarelo)")
    dar_re_meio_quarteirao()

    virar_direita()
    achar_nao_verde_alinhado()
    LOG("alinhar_caçambas: viu não verde (espera vermelho)")

    dar_re(DIST_BORDA_CAÇAMBA + DIST_EIXO_SENSOR)
    dar_meia_volta()

#! isso tá em max_cubos=2 mas na verdade só funciona com 1
def colocar_cubo_na_caçamba(cor_cubo, max_cubos=2): #! suportar 2 e 3 cubos rs
    global cubos_caçambas
    margem      = TAM_CUBO//2 if max_cubos != 1 else (TAM_CUBO*3)//2
    espaçamento = TAM_CUBO    if max_cubos == 2 else 0

    ASSERT(cor_cubo != Cor.enum.NENHUMA)
    blt.levantar_garra(hub)
    alinhar_caçambas()
    for i, (cor, dist) in enumerate(zip(cores_caçambas, DISTS_CAÇAMBAS)):
        if cor_cubo == cor:
            if cubos_caçambas[i] > max_cubos: continue

            rodas.straight(dist - DIST_BORDA_CAÇAMBA - margem
                          + cubos_caçambas[i]*(TAM_CUBO + espaçamento))
            blt.abaixar_garra(hub)
            blt.levantar_garra(hub)
            virar_direita()

            achar_nao_verde_alinhado()
            rodas.straight(DIST_VERDE_CAÇAMBA)
            blt.abrir_garra(hub)

            cubos_caçambas[i] += 1
            return

    raise SucessoOuCatástrofe("sem lugar pro cubo nas caçambas")

 #! tá empurrando
def procura(hub, pos_estimada, cores_caçambas):
    cel_incertas = pegar_celulas_incertas()
    cel_atual = pos_estimada

    #! ordenar lista com o a_estrela
    for cel_destino in cel_incertas:
        LOG("tentando de", cel_atual, "até :", cel_destino)
        imprimir_mapa()

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
        _, ori_final = achar_movimentos(restante, orientacao_estimada)
        acertar_orientacao(ori_final)

        rodas.straight(DIST_CRUZAMENTO_CUBO, then=Stop.COAST)

        cor = blt.ver_cor_cubo(hub)
        if cor == Cor.enum.NENHUMA: # não tem cubo
            LOG("procura: cel livre")
            tira_obstaculo(cel_destino)
            rodas.straight(TAM_BLOCO - DIST_CRUZAMENTO_CUBO, then=Stop.COAST)
            cel_atual = cel_destino
            continue
        if cor not in cores_caçambas:
            LOG(f"procura: cubo desconhecido cor {cor}")
            if cor == Cor.enum.BRANCO:
                bipe_cabeca(hub) #! fazer fora?
            coloca_obstaculo(cel_destino)
            dar_re(DIST_CRUZAMENTO_CUBO)
            continue

        LOG(f"procura: cubo cor {cor}")
        blt.fechar_garra(hub)
        tira_obstaculo(cel_destino)
        dar_re(DIST_CRUZAMENTO_CUBO)
        return cor, cel_atual

    imprimir_mapa()

    raise SucessoOuCatástrofe()

def descobrir_cor_caçambas():
    global cores_caçambas
    if not cores_caçambas:
        cores_caçambas = [Cor.enum.NENHUMA for i in range(NUM_CAÇAMBAS)]

    alinhar_caçambas()
    rodas.straight(DIST_EIXO_SENSOR_TRAS-10)
    virar_direita()
    achar_nao_verde_alinhado()
    rodas.straight(DIST_VERDE_CAÇAMBA-10)
    virar_esquerda()
    for i in range(NUM_CAÇAMBAS):
        cores_caçambas[i] = blt.ver_cor_caçamba(hub)
        LOG(f"Cor caçamba:", Cor.enum(cores_caçambas[i]))
        #with mudar_velocidade(rodas, 50):
        rodas.straight(TAM_CAÇAMBA+DIST_CAÇAMBA)

class teste:
    @staticmethod
    def imprimir_caçamba_para_sempre():
        while True:
            cor = blt.ver_cor_caçamba(hub)
            print(Cor.enum(cor))


if __name__ == "__main__":
    from lib.bipes import bipe_inicio, bipe_final, bipe_falha

    try:    TESTE == True
    except: TESTE = False
    try:    DEBUG == True
    except: DEBUG = False

    hub = setup()
    try:
        bipe_inicio(hub)
        if TESTE: test(hub)
        else:     main(hub)
        bipe_final(hub)
    except Exception as e:
        bipe_falha(hub)
        raise e
