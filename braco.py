from pybricks.hubs import PrimeHub

from pybricks.pupdevices import Motor, ColorSensor, UltrasonicSensor
from pybricks.parameters import Port, Button, Color, Direction
from pybricks.tools      import wait, StopWatch

import bluetooth as blt

import cores
import garra

#! se a gente girar a garra na mão, mesmo resetando a cabeça, o estado da garra no braço se mantém e a gente se fode.

def LOG(*args, print=print, **kwargs):
    print("braço:", *args, **kwargs)

def ERRO(*args):
    from lib.bipes import bipe_falha
    LOG("ERRO:", *args); bipe_falha(hub)

def setup():
    global hub, motor_garra, motor_vertical, sensor_cor_frente, ultra_dir, ultra_esq
    global garra_fechada, garra_levantada

    hub = PrimeHub(broadcast_channel=blt.TX_BRACO,
                   observe_channels=[blt.TX_CABECA])
    nome, bat = hub.system.name(), hub.battery.voltage()

    LOG(f"{nome}: {bat}mV")
    while nome != "spike0":
        hub.speaker.beep(frequency=1024)
        wait(200)
    else:
        hub.light.blink(Color.ORANGE, [100,50,200,100])
    blt.init(hub)

    motor_garra       = Motor(Port.B, Direction.COUNTERCLOCKWISE)
    motor_vertical    = Motor(Port.A, Direction.COUNTERCLOCKWISE)

    sensor_cor_frente = ColorSensor(Port.D)

    garra_fechada = False
    garra_levantada = False

    hub.system.set_stop_button((Button.CENTER,))

    LOG("ligando arduino")
    try:
        from pybricks.pupdevices import DCMotor as DC
        arduino5V = DC(Port.F).dc(100)
    except OSError:
        ERRO("ARDUINO NÃO CONECTADO!")

    return hub

def main(hub):
    global garra_fechada, garra_levantada

    cmd = None
    while True:
        antes, cmd = cmd, hub.ble.observe(blt.TX_CABECA)
        if cmd is not None:
            comando, *args = cmd
        else:
            if antes != None:
                LOG("recebendo nada")
            continue

        if cmd != antes:
            LOG(f"{blt.comando_bt(comando)}{args}")

        if   comando == blt.comando_bt.fecha_garra:
            if not garra_fechada:
                LOG("fechando")
                garra.fecha_garra(motor_garra)
                garra_fechada = True
            hub.ble.broadcast((blt.comando_bt.fechei,))
        elif comando == blt.comando_bt.abre_garra:
            if garra_fechada:
                LOG("abrindo")
                garra.abre_garra(motor_garra)
                garra_fechada = False
            hub.ble.broadcast((blt.comando_bt.abri,))

        elif comando == blt.comando_bt.levanta_garra:
            if not garra_levantada:
                LOG("levantando")
                garra.levanta_garra(motor_vertical)
                garra_levantada = True
            hub.ble.broadcast((blt.comando_bt.levantei,))
        elif comando == blt.comando_bt.abaixa_garra:
            if garra_levantada:
                LOG("abaixando")
                garra.abaixa_garra(motor_vertical)
                garra_levantada = False
            hub.ble.broadcast((blt.comando_bt.abaixei,))
            
        elif comando == blt.comando_bt.ver_cor_cubo:
            #! reclassificar cor com hsv se der NONE
            cor = sensor_cor_frente.color()
            hub.ble.broadcast((blt.comando_bt.cor_cubo, cores.Color2cor(cor)))
        elif comando == blt.comando_bt.ver_hsv_cubo:
            cor = sensor_cor_frente.hsv()
            hub.ble.broadcast((blt.comando_bt.hsv_cubo, cores.Color2tuple(cor)))

def test(hub):
    ... # testar coisas aqui sem mudar o resto do código

if __name__ == "__main__":
    from lib.bipes import bipe_inicio, bipe_final

    try:    TESTE == True
    except: TESTE = False

    hub = setup()
    while True:
      try:
        bipe_inicio(hub)
        if TESTE: test(hub)
        else:     main(hub)
        bipe_final(hub)
      except Exception as e:
        ERRO(f"{e}")
        continue

