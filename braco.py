from pybricks.hubs import PrimeHub

from pybricks.pupdevices import Motor, ColorSensor, UltrasonicSensor
from pybricks.parameters import Port, Button, Color, Direction
from pybricks.tools      import wait, StopWatch

import bluetooth as blt

import globais
import cores
import garra

from globais import bipes
from globais import LOG, ERRO, ASSERT


#! se a gente girar a garra na mão, mesmo resetando a cabeça, o estado da garra no braço se mantém e a gente se fode.

def setup():
    global garra_fechada, garra_levantada
    global sensor_cor_frente

    garra_levantada = False
    garra_fechada   = False

    hub = PrimeHub(broadcast_channel=blt.TX_BRACO,
                   observe_channels=[blt.TX_CABECA])
    globais.init(hub, TESTE, DEBUG, nome="braço")

    globais.motor_garra    = Motor(Port.B, Direction.COUNTERCLOCKWISE)
    globais.motor_vertical = Motor(Port.A, Direction.COUNTERCLOCKWISE)

    sensor_cor_frente = ColorSensor(Port.D)

    LOG("ligando arduino")
    try:
        from pybricks.pupdevices import DCMotor
        arduino = DCMotor(Port.F); arduino.dc(100)
        LOG("arduino ligado")
    except OSError:
        ERRO("ARDUINO NÃO CONECTADO!")

    hub.system.set_stop_button((Button.CENTER,))
    return hub

def main():
    global garra_fechada, garra_levantada

    cmd = None
    while True:
        antes, cmd = cmd, hub.ble.observe(blt.TX_CABECA)
        if cmd is not None:
            comando, *args = cmd
        else: continue

        if cmd != antes:
            LOG(f"{blt.cmd(comando)}{args}")

        if   comando == blt.cmd.fecha_garra:
            if not garra_fechada:
                LOG("fechando")
                garra.fecha_garra()
                garra_fechada = True
            hub.ble.broadcast((blt.cmd.fechei,))
        elif comando == blt.cmd.abre_garra:
            if garra_fechada:
                LOG("abrindo")
                garra.abre_garra()
                garra_fechada = False
            hub.ble.broadcast((blt.cmd.abri,))

        elif comando == blt.cmd.levanta_garra:
            if not garra_levantada:
                LOG("levantando")
                garra.levanta_garra()
                garra_levantada = True
            hub.ble.broadcast((blt.cmd.levantei,))
        elif comando == blt.cmd.abaixa_garra:
            if garra_levantada:
                LOG("abaixando")
                garra.abaixa_garra()
                garra_levantada = False
            hub.ble.broadcast((blt.cmd.abaixei,))
            
        elif comando == blt.cmd.ver_cor_cubo:
            #! reclassificar cor com hsv se der NONE
            cor = sensor_cor_frente.color()
            hub.ble.broadcast((blt.cmd.cor_cubo, cores.Color2cor(cor)))
        elif comando == blt.cmd.ver_hsv_cubo:
            cor = sensor_cor_frente.hsv()
            hub.ble.broadcast((blt.cmd.hsv_cubo, cores.Color2tuple(cor)))

def test():
    ... # testar coisas aqui sem mudar o resto do código

if __name__ == "__main__":
    try:    TESTE == True
    except: TESTE = False
    try:    DEBUG == True
    except: DEBUG = False

    hub = setup()
    while True:
      try:
        bipes.inicio()
        if TESTE: test()
        else:     main()
        bipes.final()
      except Exception as e:
        ERRO(f"{e}")
        continue

