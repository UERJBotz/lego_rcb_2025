from comum import globais

from lib.polyfill import Enum


SILENCIOSO = False

TX_CABECA = 24
TX_BRACO  = 69
TX_RABO   = 32

cmd = Enum("cmd", [
    "fecha_garra",
    "abre_garra",
    "levanta_garra",
    "abaixa_garra",
    "ver_cor_cubo",
    "ver_hsv_cubo",
    "ver_distancias",
    "ver_cor_caçamba",
    "ver_dist_caçamba",
])

rsp = Enum("rsp", [
    "fechei",
    "abri",
    "levantei",
    "abaixei",
    "cor_cubo",
    "hsv_cubo",
    "distancias",
    "cor_caçamba",
    "dist_caçamba",
])

def enviar_comando(*comando):
    if not SILENCIOSO: print(f"enviar_comando: {cmd(comando)}{comando}")
    globais.ble.broadcast(tuple(comando))

def esperar_resposta(esperado, canal=TX_BRACO):
    resposta = -1
    if not SILENCIOSO: print(f"esperar_resposta: {rsp(esperado)}")
    while resposta != esperado:
        resposta = globais.ble.observe(canal)
        if not SILENCIOSO: print(f"esperar_resposta: recebido {canal} {rsp(resposta)}{resposta}")
        if resposta is not None:
            resposta, *args = resposta
    if len(args) == 1: return args[0]
    return args

def resetar_garra():
    levantar_garra()
    fechar_garra()
    abrir_garra()

def fechar_garra():
    if not SILENCIOSO: print("fechar_garra:")
    enviar_comando(cmd.fecha_garra)
    return esperar_resposta(rsp.fechei)

def abrir_garra():
    if not SILENCIOSO: print("abrir_garra:")
    enviar_comando(cmd.abre_garra)
    return esperar_resposta(rsp.abri)

def levantar_garra():
    if not SILENCIOSO: print("levantar_garra:")
    enviar_comando(cmd.levanta_garra)
    return esperar_resposta(rsp.levantei)

def abaixar_garra():
    if not SILENCIOSO: print("abaixar_garra:")
    enviar_comando(cmd.abaixa_garra)
    return esperar_resposta(rsp.abaixei)

def ver_cor_cubo():
    if not SILENCIOSO: print("ver_cor_cubo:")
    enviar_comando(cmd.ver_cor_cubo)
    return esperar_resposta(rsp.cor_cubo)

def ver_hsv_cubo():
    if not SILENCIOSO: print("ver_hsv_cubo:")
    enviar_comando(cmd.ver_hsv_cubo)
    return esperar_resposta(rsp.hsv_cubo)

def ver_distancias():
    if not SILENCIOSO: print("ver_distancias:")
    enviar_comando(cmd.ver_distancias)
    return esperar_resposta(rsp.distancias)

def ver_cor_caçamba():
    if not SILENCIOSO: print("ver_cor_caçamba:")
    #enviar_comando(cmd.ver_cor_caçamba)
    return esperar_resposta(rsp.cor_caçamba, canal=TX_RABO)

def ver_dist_caçamba():
    if not SILENCIOSO: print("ver_dist_caçamba:")
    enviar_comando(cmd.ver_dist_caçamba)
    return esperar_resposta(rsp.dist_caçamba)

