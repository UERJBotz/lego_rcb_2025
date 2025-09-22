from lib.polyfill import Enum
from pybricks.parameters import Button

TX_CABECA = 24
TX_BRACO  = 69

comando_bt = Enum("comando_bt", ["fecha_garra",
                                 "abre_garra",
                                 "levanta_garra",
                                 "abaixa_garra",
                                 "ver_cor_passageiro",
                                 "ver_hsv_passageiro",
                                 "ver_distancias",
                                 "ler_botoes",
                                 #! fazer um enum comandos e outro respostas
                                 "fechei",
                                 "abri",
                                 "levantei",
                                 "abaixei",
                                 "cor_passageiro",
                                 "hsv_passageiro",
                                 "distancias",
                                 "li_botoes",
                                 ])

Botão = Enum("Botão", ["esquerdo",
                       "direito",
                       "bluetooth",
                       "centro"])

def Button2Botão(bot: Button):
    return {
        Button.BLUETOOTH: Botão.bluetooth,
        Button.LEFT: Botão.esquerdo,
        Button.RIGHT: Botão.direito,
        Button.CENTER: Botão.centro,
    }.get(bot)

def esperar_resposta(hub, esperado, canal=TX_BRACO):
    comando = -1
    while comando != esperado:
        comando = hub.ble.observe(canal)
        if comando is not None:
            comando, *args = comando
    return args

def resetar_garra(hub):
    blt.levantar_garra(hub)
    blt.fechar_garra(hub)
    blt.abrir_garra(hub)
    blt.abaixar_garra(hub)

def fechar_garra(hub):
    print("fechar_garra:")
    hub.ble.broadcast((comando_bt.fecha_garra,))
    return esperar_resposta(hub, comando_bt.fechei)

def abrir_garra(hub):
    print("abrir_garra:")
    hub.ble.broadcast((comando_bt.abre_garra,))
    return esperar_resposta(hub, comando_bt.abri)

def levantar_garra(hub):
    pass


def ler_botoes(hub):
    print("ler:")
    hub.ble.broadcast((comando_bt.ler_botoes,))
    return esperar_resposta(hub, comando_bt.li_botoes)