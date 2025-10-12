import globais

from lib.polyfill import Enum

TX_CABECA = 24
TX_BRACO  = 69
TX_RABO   = 32

cmd = Enum("cmd", ["fecha_garra",
                   "abre_garra",
                   "levanta_garra",
                   "abaixa_garra",
                   "ver_cor_cubo",
                   "ver_hsv_cubo",
                   "ver_distancias",
                   "ver_cor_caçamba",
                   #! fazer um enum comandos e outro respostas
                   "fechei",
                   "abri",
                   "levantei",
                   "abaixei",
                   "cor_cubo",
                   "hsv_cubo",
                   "distancias",
                   "cor_caçamba"])


def enviar_comando(*comando):
    globais.ble.broadcast(tuple(comando))

def esperar_resposta(esperado, canal=TX_BRACO):
    comando = -1
    while comando != esperado:
        comando = globais.ble.observe(canal)
        if comando is not None:
            comando, *args = comando
    return args

def resetar_garra():
    levantar_garra()
    fechar_garra()
    abrir_garra()

def fechar_garra():
    print("fechar_garra:")
    enviar_comando(cmd.fecha_garra)
    return esperar_resposta(cmd.fechei)

def abrir_garra():
    print("abrir_garra:")
    enviar_comando(cmd.abre_garra)
    return esperar_resposta(cmd.abri)

def levantar_garra():
    print("levantar_garra:")
    enviar_comando(cmd.levanta_garra)
    return esperar_resposta(cmd.levantei)

def abaixar_garra():
    print("abaixar_garra:")
    enviar_comando(cmd.abaixa_garra)
    return esperar_resposta(cmd.abaixei)

def ver_cor_cubo():
    print("ver_cor_cubo:")
    enviar_comando(cmd.ver_cor_cubo)
    return esperar_resposta(cmd.cor_cubo)[0]

def ver_hsv_cubo():
    print("ver_hsv_cubo:")
    enviar_comando(cmd.ver_hsv_cubo)
    return esperar_resposta(cmd.hsv_cubo)

def ver_distancias():
    print("ver_distancias:")
    enviar_comando(cmd.ver_distancias)
    return esperar_resposta(cmd.distancias)

def ver_cor_caçamba():
    print("ver_cor_caçamba:")
    #enviar_comando(cmd.ver_cor_caçamba)
    return esperar_resposta(cmd.cor_caçamba, canal=TX_RABO)[0]

