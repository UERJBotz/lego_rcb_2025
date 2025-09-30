import blt

from machine import UART
from bleradio import BLERadio

class NoneHub():
    def __init__(self, broadcast_channel=None,
                       observe_channels=[]):
        self.ble = BLERadio(broadcast_channel,
                            observe_channels)

def setup():
    global hub, uart
    uart = UART(1, 115200) 
    uart.init(115200, tx=21, rx=20)
    hub = NoneHub(broadcast_channel=blt.TX_RABO,
                  observe_channels=[blt.TX_CABECA])
    blt.init(hub)
    return hub

def main(hub):
    while True:
        if uart.any():
            cor = ord(uart.read(1))
            print(cor)

            hub.ble.broadcast((blt.comando_bt.cor_cacamba, cor))

        comando = hub.ble.observe(blt.TX_CABECA)
        if comando is not None:
            print(f"rabo: {comando}");
            comando, *args = comando
        else: continue


if __name__ == "__main__":
    hub = setup()
    main(hub)
