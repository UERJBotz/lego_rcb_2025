from pybricks.tools import wait

# cabeça
rodas = None
sensor_cor_esq = None
sensor_cor_dir = None

# braço
motor_garra = None
motor_vertical = None
sensor_cor_frente = None

# comum
hub = None
ble = None
name = None
nome = None


def init(_hub, _teste, _debug, _ble=None):
    global hub, ble
    hub = _hub
    ble = _ble or _hub.ble

    global TESTE, DEBUG
    TESTE = _teste
    DEBUG = _debug

    global name, nome
    name = hub.system.name()
    if   name == "spike0": nome = "braço"
    elif name == "spike1": nome = "cabeça"
    else:
        ASSERT(False, "hub desconhecido")


class bipes:
    inicio = lambda: hub.speaker.beep(frequency=500, duration=100)
    final  = lambda: hub.speaker.beep(frequency=250, duration=250)

    separador  = lambda: hub.speaker.beep(frequency=600, duration=200)
    calibracao = lambda: hub.speaker.beep(frequency=300, duration=100)
    cabeca     = lambda: hub.speaker.beep(frequency=600, duration=100)

    falha      = lambda: (hub.speaker.beep(frequency=800, duration=500), wait(200),
                          hub.speaker.beep(frequency=800, duration=500),)


def LOG(*args, print=print, **kwargs):
    print(f"{nome}:", *args, **kwargs)

def ERRO(*args, bipar=True):
    LOG("ERRO:", *args);
    if bipar: bipes.falha()

def ASSERT(cond, texto=None):
    if DEBUG: assert cond, texto
    elif not cond:
        ERRO(f"assert '{texto}' falhou", bipar=DEBUG)
    return cond



