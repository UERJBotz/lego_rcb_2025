from lib.polyfill import Enum

TX_CABECA = 24
TX_BRACO  = 69
TX_RABO   = 32

comando_bt = Enum("comando_bt", ["fecha_garra",
                                 "abre_garra",
                                 "levanta_garra",
                                 "abaixa_garra",
                                 "ver_cor_cubo",
                                 "ver_hsv_cubo",
                                 "ver_distancias",
                                 #! fazer um enum comandos e outro respostas
                                 "fechei",
                                 "abri",
                                 "levantei",
                                 "abaixei",
                                 "cor_cubo",
                                 "cor_cacamba",
                                 "hsv_cubo",
                                 "distancias"])

#! tirar hub dos argumentos

def init(hub):
    global ble
    ble = hub.ble

def esperar_resposta(hub, esperado, canal=TX_BRACO):
    comando = -1
    while comando != esperado:
        comando = ble.observe(canal)
        if comando is not None:
            comando, *args = comando
    return args

def resetar_garra(hub):
    levantar_garra(hub)
    fechar_garra(hub)
    abrir_garra(hub)
    abaixar_garra(hub)

def fechar_garra(hub):
    print("fechar_garra:")
    ble.broadcast((comando_bt.fecha_garra,))
    return esperar_resposta(hub, comando_bt.fechei)

def abrir_garra(hub):
    print("abrir_garra:")
    ble.broadcast((comando_bt.abre_garra,))
    return esperar_resposta(hub, comando_bt.abri)

def levantar_garra(hub):
    print("levantar_garra:")
    ble.broadcast((comando_bt.levanta_garra,))
    return esperar_resposta(hub, comando_bt.levantei)

def abaixar_garra(hub):
    print("abaixar_garra:")
    ble.broadcast((comando_bt.abaixa_garra,))
    return esperar_resposta(hub, comando_bt.abaixei)

def ver_cor_cubo(hub):
    print("ver_cor_cubo:")
    ble.broadcast((comando_bt.ver_cor_cubo,))
    return esperar_resposta(hub, comando_bt.cor_cubo)[0]

def ver_hsv_cubo(hub):
    print("ver_hsv_cubo:")
    ble.broadcast((comando_bt.ver_hsv_cubo,))
    return esperar_resposta(hub, comando_bt.hsv_cubo)

def ver_distancias(hub):
    print("ver_distancias:")
    ble.broadcast((comando_bt.ver_distancias,))
    return esperar_resposta(hub, comando_bt.distancias)
