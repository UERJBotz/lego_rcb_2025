from pybricks.hubs import PrimeHub

from pybricks.pupdevices import Motor, ColorSensor, UltrasonicSensor
from pybricks.parameters import Port, Button, Color, Direction
from pybricks.tools      import wait, StopWatch

import bluetooth as blt

import cores
import garra

def setup():
    global hub, motor_garra, motor_vertical, sensor_cor_frente, ultra_dir, ultra_esq
    global garra_fechada, garra_levantada

    hub = PrimeHub(broadcast_channel=blt.TX_BRACO,
                   observe_channels=[blt.TX_CABECA])
    nome, bat = hub.system.name(), hub.battery.voltage()

    print(f"{nome}: {bat}mV")
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

    from pybricks.pupdevices import DCMotor
    arduino5V = DCMotor(Port.F).dc(100)

    return hub

def main(hub):
    global garra_fechada, garra_levantada

    while True:
        comando = hub.ble.observe(blt.TX_CABECA)
        if comando is not None:
            print(comando)
            comando, *args = comando
        else: continue

        if   comando == blt.comando_bt.fecha_garra:
            print("pediu fecho")
            if not garra_fechada:
                print("fechando")
                garra.fecha_garra(motor_garra)
                garra_fechada = True
            hub.ble.broadcast((blt.comando_bt.fechei,))
        elif comando == blt.comando_bt.abre_garra:
            print("pediu abre")
            if garra_fechada:
                print("abrindo")
                garra.abre_garra(motor_garra)
                garra_fechada = False
            hub.ble.broadcast((blt.comando_bt.abri,))

        elif comando == blt.comando_bt.levanta_garra:
            print("pediu levanto")
            if not garra_levantada:
                print("levantando")
                garra.levanta_garra(motor_vertical)
                garra_levantada = True
            hub.ble.broadcast((blt.comando_bt.levantei,))
        elif comando == blt.comando_bt.abaixa_garra:
            print("pediu abaixo")
            if garra_levantada:
                print("abaixando")
                garra.abaixa_garra(motor_vertical)
                garra_levantada = False
            hub.ble.broadcast((blt.comando_bt.abaixei,))
            
        elif comando == blt.comando_bt.ver_cor_cubo:
            print("pediu cor")
            cor = sensor_cor_frente.color() #! reclassificar co hsv se der NONE
            hub.ble.broadcast((blt.comando_bt.cor_cubo, cores.Color2cor(cor)))
        elif comando == blt.comando_bt.ver_hsv_cubo:
            print("pediu hsv")
            cor = sensor_cor_frente.hsv()
            hub.ble.broadcast((blt.comando_bt.hsv_cubo, cores.Color2tuple(cor)))

if __name__ == "__main__":
    from lib.bipes import bipe_inicio, bipe_final, bipe_falha
    hub = setup()
    while True:
      try:
          bipe_inicio(hub)
          main(hub)
          bipe_final(hub)
      except Exception as e:
          bipe_falha(hub)
          print(f"{e}")
          continue

