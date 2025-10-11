import blt

from time import ticks_ms as millis, sleep_ms as delay
from machine import UART, Pin
from bleradio import BLERadio

from lib.polyfill import Enum

Cor = Enum("Cor", ["NENHUMA",
                   "PRETO",
                   "AZUL",
                   "VERDE",
                   "AMARELO",
                   "VERMELHO",
                   "BRANCO",
                   "MARROM"])

class Led(Pin):
    def __init__(self, pin):
        super().__init__(pin, Pin.OUT)
    def on(self):  self.value(0)
    def off(self): self.value(1)

class NoneHub():
    def __init__(self, broadcast_channel=None,
                       observe_channels=[]):
        self.ble = BLERadio(broadcast_channel,
                            observe_channels)

def setup():
    global hub, timer, uart, led

    uart = UART(1, 115200) 
    uart.init(115200, tx=21, rx=10)

    led = Led(8)
    led.on()

    hub = NoneHub(broadcast_channel=blt.TX_RABO,
                  observe_channels=[blt.TX_CABECA])
    blt.init(hub)
    timer = millis()
    return hub

def main(hub):
    global timer

    while True:
        if uart.any():
            cor = ord(uart.read(1))
            hub.ble.broadcast((blt.comando_bt.cor_caçamba, cor))
            print(Cor(cor))

        if (millis() - timer) > 1000:
            timer = millis()
            led.toggle()

        comando = hub.ble.observe(blt.TX_CABECA)
        if comando is not None:
            print(f"rabo: {comando}")
            #comando, *args = comando
        else: continue


if __name__ == "__main__":
    while True:
        try:
            hub = setup()
            main(hub)
        except Exception as e:
            print(f"{e}")
            continue
