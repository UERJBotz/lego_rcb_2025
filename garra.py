from pybricks.parameters import Port, Stop
from pybricks.tools      import wait

from comum import globais

RAIO_ENGRENAGEM  = 6#mm
DIST_SUBIR_GARRA = 100#mm

ANG_SUBIR_GARRA = DIST_SUBIR_GARRA*RAIO_ENGRENAGEM

def fecha_garra(vel=240):
    globais.motor_garra.run_until_stalled(vel, then=Stop.COAST, duty_limit=None)
    globais.motor_garra.run_angle(vel, 30, then=Stop.COAST, wait=False)

def abre_garra(vel=240, ang_volta=60): #ang_volta=72
    globais.motor_garra.run_angle(vel, -ang_volta, then=Stop.COAST, wait=True)

def levanta_garra(vel=240):
    globais.motor_vertical.run_until_stalled(vel, then=Stop.COAST, duty_limit=None)
    #globais.motor_vertical.run_angle(vel, ANG_SUBIR_GARRA, then=Stop.COAST, wait=True)

def abaixa_garra(vel=240):
    #! globais.motor_vertical.run_until_stalled(-vel, then=Stop.COAST, duty_limit=None)
    globais.motor_vertical.run_angle(-vel, ANG_SUBIR_GARRA, then=Stop.COAST, wait=True)
