from pybricks.hubs import PrimeHub

from pybricks.pupdevices import Motor, ColorSensor, UltrasonicSensor
from pybricks.parameters import Port, Stop, Side, Direction, Button, Color

from pybricks.tools      import wait, StopWatch
from pybricks.robotics   import DriveBase

from lib.bipes    import bipe_calibracao, bipe_cabeca, bipe_separador, musica_vitoria, musica_derrota

from lib.caminhos import achar_movimentos, tipo_movimento, tira_obstaculo

from urandom import choice

import gui
import cores
import bluetooth as blt

VEL_ALINHAR = 80
VEL_ANG_ALINHAR = 20
GIRO_MAX_ALINHAR = 70 #!80

TAM_QUARTEIRAO = 300
TAM_BLOCO = TAM_QUARTEIRAO//2
TAM_FAIXA = 20

PISTA_TODA = TAM_QUARTEIRAO*6

DIST_EIXO_SENSOR = 45


#! checar stall: jogar exceção
#! checar cor errada no azul
#! tem um lugar começo do achar azul que tem que dar ré


def setup():
    global hub, rodas
    global sensor_cor_esq, sensor_cor_dir, sensor_ultra_esq, sensor_ultra_dir
    global botao_calibrar, orientacao_estimada
    global rodas_conf_padrao, vels_padrao, vel_padrao, vel_ang_padrao #! fazer um dicionário e concordar com mudar_velocidade
    
    hub = PrimeHub(broadcast_channel=blt.TX_CABECA,
                   observe_channels=[blt.TX_BRACO,
                                     blt.TX_RABO])
    nome, bat = hub.system.name(), hub.battery.voltage()

    print(f"{nome}: {bat}mV")
    while nome != "spike1":
        hub.speaker.beep(frequency=1024); wait(200)
    else:
        hub.light.blink(Color.RED, [100,50,200,100])
    blt.init(hub)

    hub.display.orientation(Side.BOTTOM)
    hub.system.set_stop_button((Button.CENTER, Button.BLUETOOTH))

    orientacao_estimada = ""

    sensor_cor_esq = ColorSensor(Port.D)
    sensor_cor_dir = ColorSensor(Port.C)

    roda_esq = Motor(Port.B, positive_direction=Direction.COUNTERCLOCKWISE)
    roda_dir = Motor(Port.A, positive_direction=Direction.CLOCKWISE)

    rodas = DriveBase(roda_esq, roda_dir,
                      wheel_diameter=88, axle_track=145.5) #! recalibrar

    botao_calibrar = Button.CENTER

    rodas_conf_padrao = rodas.settings() #! CONSTANTIZAR
    vel_padrao     = rodas_conf_padrao[0]
    vel_ang_padrao = rodas_conf_padrao[2]
    vels_padrao = vel_padrao, vel_ang_padrao

    return hub

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

def inverte_orientacao():
    global orientacao_estimada
    if orientacao_estimada == "N": orientacao_estimada = "S"
    if orientacao_estimada == "S": orientacao_estimada = "N"
    if orientacao_estimada == "L": orientacao_estimada = "O"
    if orientacao_estimada == "O": orientacao_estimada = "L"

def dar_meia_volta():
    inverte_orientacao()
    rodas.turn(180)
    
def virar_direita():
    global orientacao_estimada
    if   orientacao_estimada == "N": orientacao_estimada = "L"
    elif orientacao_estimada == "S": orientacao_estimada = "O"
    elif orientacao_estimada == "L": orientacao_estimada = "S"
    elif orientacao_estimada == "O": orientacao_estimada = "N"

    print(f"virar_direita: {orientacao_estimada=}")
    rodas.turn(90)

def virar_esquerda():
    global orientacao_estimada
    if   orientacao_estimada == "N": orientacao_estimada = "O"
    elif orientacao_estimada == "S": orientacao_estimada = "L"
    elif orientacao_estimada == "L": orientacao_estimada = "N"
    elif orientacao_estimada == "O": orientacao_estimada = "S"

    print(f"virar_esquerda: {orientacao_estimada=}")
    rodas.turn(-90)

DIST_PARAR=-0.4
def parar():
    rodas.straight(DIST_PARAR)
    rodas.stop()
ANG_PARAR=-0.0
def parar_girar():
    rodas.turn(ANG_PARAR)
    rodas.stop()

def dar_re(dist):
    rodas.straight(-dist)

def dar_re_meio_quarteirao():
    dar_re(TAM_BLOCO - DIST_EIXO_SENSOR)

#! provavelmente mudar andar_ate pra receber uma fn -> bool e retornar só bool, dist (pegar as informações extras na própria função)

def ver_nao_pista() -> tuple[bool, tuple[Color, hsv], tuple[Color, hsv]]: # type: ignore
    #! usar verificar_cor em vez disso?
    esq, dir = cores.todas(sensor_cor_esq, sensor_cor_dir)
    return ((not cores.pista_unificado(*esq) or not cores.pista_unificado(*dir)),
            esq, dir)

def ver_nao_verde() -> tuple[bool, tuple[Color, hsv], tuple[Color, hsv]]: # type: ignore
    #! usar verificar_cor em vez disso?
    esq, dir = cores.todas(sensor_cor_esq, sensor_cor_dir)
    print(f"esq: {esq}, dir: {dir}")
    return ((not cores.area_livre_unificado(*esq) or not cores.area_livre_unificado(*dir)),
            esq, dir)

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
            print("andar_ate_cor: andou demais")
            return False, (None,) #ou(res, extra)
        else: 
            print(res)
            assert False

def cor_final(retorno):
    achou, extra = retorno

    if achou: return extra
    else:     return cores.todas(sensor_cor_esq, sensor_cor_dir)

def achar_limite() -> tuple[tuple[Color, hsv], tuple[Color, hsv]]: # type: ignore
    return cor_final(andar_ate_idx(ver_nao_pista))

def achar_diferente() -> tuple[tuple[Color, hsv], tuple[Color, hsv]]:
    return cor_final(andar_ate_idx(ver_nao_verde))

def alinha_parede(vel, vel_ang, giro_max=45,
                  _cor_unificado=cores.area_livre_unificado,
                  _ver_nao_x=ver_nao_verde
                  ) -> bool:
    alinhado_parede = lambda esq, dir: not _cor_unificado(*esq) and not _cor_unificado(*dir)
    alinhado_pista  = lambda esq, dir: _cor_unificado(*esq) and _cor_unificado(*dir)

    with mudar_velocidade(rodas, vel, vel_ang):
        parou, extra = andar_ate_idx(_ver_nao_x, dist_max=TAM_BLOCO)
        if not parou:
            (dist,) = extra
            print(f"alinha_parede: reto pista {dist}")
            return False # viu só branco, não sabemos se tá alinhado
    
        (esq, dir) = extra
        if  alinhado_parede(esq, dir):
            print("alinha_parede: reto não pista")
            return True
        elif not _cor_unificado(*dir):
            print("alinha_parede: torto pra direita")
            GIRO = -giro_max
        elif not _cor_unificado(*esq):
            print("alinha_parede: torto pra esquerda")
            GIRO = giro_max

        rodas.turn(GIRO, wait=False) #! fazer gira_ate
        while not rodas.done():
            esq, dir = cores.todas(sensor_cor_esq, sensor_cor_dir)
            print(esq, dir)
            if  alinhado_parede(esq, dir):
                print("alinha_parede: alinhado parede")
                parar_girar()
                return True # deve tar alinhado
            elif alinhado_pista(esq, dir):
                print("alinha_parede: alinhado pista")
                parar_girar()
                return False #provv alinhado, talvez tentar de novo
        return False # girou tudo, não sabemos se tá alinhado

def alinhar(max_tentativas=4, virar=True,
                              vel=VEL_ALINHAR, vel_ang=VEL_ANG_ALINHAR,
                              giro_max=GIRO_MAX_ALINHAR) -> None:
    for _ in range(max_tentativas): #! esqueci mas tem alguma coisa
        rodas.reset()
        alinhou = alinha_parede(vel, vel_ang, giro_max=giro_max)

        ang  = rodas.angle()
        dist = rodas.distance()
        with mudar_velocidade(rodas, vel, vel_ang):
            rodas.turn(-ang)
            dar_re(dist)
            rodas.turn(ang)

        if alinhou: return
        else:
            if virar: virar_direita() #! testar agora
            continue
    return

def alinha_limite(max_tentativas=3, vel=VEL_ALINHAR, vel_ang=VEL_ANG_ALINHAR, giro_max=70) -> None:
    for _ in range(max_tentativas):
        rodas.reset()
        dar_re_meio_quarteirao()

        alinhou = alinha_parede(vel, vel_ang, giro_max=giro_max)
        ang  = rodas.angle()
        dist = rodas.distance()
        if alinhou: return
        else:
            with mudar_velocidade(rodas, 80, 30):
                rodas.turn(-ang)
                dar_re(dist)
                rodas.turn(ang)
    return

def seguir_caminho(pos, obj): #! lidar com outras coisas
    def interpretar_movimento(mov):
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
            print(f"seguir_caminho: {tipo_movimento(mov)}")
            interpretar_movimento(mov)
            yield rodas.distance()

    movs, ori_final = achar_movimentos(pos, obj, orientacao_estimada)
    #print(*(tipo_movimento(mov) for mov in movs))

    for _ in interpretar_caminho(movs):
        while not rodas.done(): pass
        
    while orientacao_estimada != ori_final:
        print(f"{orientacao_estimada=}, {ori_final=}")
        virar_direita()

def menu_calibracao(hub, sensor_esq, sensor_dir,
                                     botao_parar=Button.BLUETOOTH,
                                     botao_aceitar=Button.CENTER,
                                     botao_anterior=Button.LEFT,
                                     botao_proximo=Button.RIGHT):
    mapa_hsv = cores.mapa_hsv.copy()

    selecao = 0

    wait(150)
    while True:
        botões = gui.tela_escolher_cor(hub, cores.cor, selecao)

        if   botao_proximo  in botões:
            selecao = (selecao + 1) % len(cores.cor)
            wait(100)
        elif botao_anterior in botões:
            selecao = (selecao - 1) % len(cores.cor)
            wait(100)

        elif botao_aceitar in botões:
            [wait(100) for _ in gui.mostrar_palavra(hub, "CAL..")]
            mapa_hsv[selecao] = (
                cores.coletar_valores(hub, botao_aceitar, dir=sensor_dir, esq=sensor_esq)
            )
            wait(150)
        elif botao_parar   in botões:
            wait(100)
            return mapa_hsv

def achar_vermelho(hub) -> bool:
    esq, dir = achar_diferente(); alinhar()
    if cores.beco_unificado(*esq) and cores.beco_unificado(*dir):
        dar_re_meio_quarteirao()
        return True
    elif cores.beco_unificado(*esq):
        alinhar()
    elif cores.beco_unificado(*dir):
        alinhar()
    else:
        choice((virar_direita, virar_esquerda))()
    return False

def achar_azul(hub) -> bool:
    choice((virar_direita, virar_esquerda))()
    esq, dir = achar_diferente(); alinhar()
    if cores.azul_unificado(*esq) and cores.azul_unificado(*dir):
        dar_re_meio_quarteirao()
        return True
        #return cores.certificar(sensor_cor_esq, sensor_cor_dir, cores.beco_unificado)
    elif cores.azul_unificado(*esq):
        alinhar()
    elif cores.azul_unificado(*dir):
        alinhar()
    else:
        dar_re_meio_quarteirao()
        dar_meia_volta()
    return False


def posicionamento_inicial(hub):
    #! alinhar()
    achou_vermelho = False
    while not achou_vermelho:
        achou_vermelho = achar_vermelho(hub)
    bipe_separador(hub)
    print("achou vermelho")

    achou_azul = False
    while not achou_azul:
        achou_azul = achar_azul(hub)
    bipe_separador(hub)
    print("achou azul")
    reseta_xy(hub) # vai para o 0,0 do verde
    return descobrir_cor_caçambas(hub)

def procura_inicial(hub, xy, caçambas): #! considerar inimigo
    entra_primeira_rua(hub)

    x, _ = xy #! para procura genérico, usar y também
    i, extra = andar_ate_idx(ver_cubo_perto, ver_nao_pista)
    while i == 2:
        x += 2 #! para procura genérico, considerar orientação
        i, extra = andar_ate_idx(ver_cubo_perto, ver_nao_pista)
    assert i == 1

    cor = extra
    if cor in caçambas:
        pegar_cubo(hub)
        dar_re_até_verde(hub, xy) #! fazer_caminho_contrário(hub) #! voltar_para_verde(hub, xy)
        return cor, xy
    else:
        fazer_caminho_contrário(hub) #! voltar_para_verde(hub, xy)
        xy = andar_1_quarteirão_no_eixo_y(hub, xy)
        return procura_inicial(hub, xy, caçambas)

def main(hub):
    global orientacao_estimada
    crono = StopWatch()
    while crono.time() < 100: #! ativar calibração quando for usar
        botões = hub.buttons.pressed()
        if botao_calibrar in botões:
            bipe_calibracao(hub)
            #! levar os dois sensores em consideração separadamente
            mapa_hsv = menu_calibracao(hub, sensor_cor_esq, sensor_cor_dir)
            cores.repl_calibracao(mapa_hsv)#, lado="esq")
            return
    hub.system.set_stop_button((Button.BLUETOOTH,))

    blt.resetar_garra(hub)
    
    caçambas = posicionamento_inicial(hub)
    cor, xy = procura_inicial(hub, 00, caçambas)
    coloca_cubo_na_caçamba(hub, cor, xy, caçambas)
    procura(hub)

if __name__ == "__main__":
    from lib.bipes import bipe_inicio, bipe_final, bipe_falha
    hub = setup()
    try:
        bipe_inicio(hub)
        main(hub)
        bipe_final(hub)
    except Exception as e:
        bipe_falha(hub)
        raise e
