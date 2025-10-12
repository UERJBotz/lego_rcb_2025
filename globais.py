from pybricks.tools import wait

# cabeça
rodas = None

# braço
motor_garra = None
motor_vertical = None

# comum
hub = None
ble = None
name = None
nome = None

def _init(_hub, _teste, _debug, _nome, _ble=None):
    global hub, ble
    hub = _hub
    ble = _ble or _hub.ble

    global TESTE, DEBUG
    TESTE = _teste
    DEBUG = _debug

    global name, nome
    name = hub.system.name()
    nome = _nome

def init(hub, *args, nome=None, **kwargs, ble=None):
    _init(hub, *args, _nome=nome, **kwargs, _ble=ble)

    LOG(f"{name}: {hub.battery.voltage()}mV")
    if   nome == "braço":  esperado = "spike0"
    elif nome == "cabeça": esperado = "spike1"
    elif nome == "rabo":   esperado = "supermini0"
    else:
        ASSERT(False, "nome de robô inesperado")
        esperado = None

    while name != esperado:
        hub.speaker.beep(frequency=1024); wait(200)
    else:
        hub.light.blink(Color.ORANGE, [100,50,200,100])


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



