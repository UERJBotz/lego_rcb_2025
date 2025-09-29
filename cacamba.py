class Cacamba:
    def __init__(self):
        self.cor
        self.pos
        self.cubos

dist_borda = 0#mudar
dist_sensor = 0#mudar
dist_cacamba = 160
dist_cubo = 50

def vetor_cacambas():
    cacambas = []
    for i in range(6):
        new_cacamba = Cacamba()
        new_cacamba.pos = dist_cacamba*i + dist_borda*(i+1) - dist_sensor
        new_cacamba.cubos = 0
        cacambas.append(new_cacamba)
    return cacambas

#começar da linha ate dist cacamba i - dist traseira ate sensor
def alinhar_cacambas(sensor_cor, orientacao_estimada): 
    '''se coloca virado ao norte, dps
        reto até amarelo vira reto até vermelho, vira vira,
        passar sensor esquerdo'''
    if (orientacao_estimada == 'S'):
        virar_esquerda()
        virar_esquerda()
    if (orientacao_estimada == 'L'):
        virar_esquerda()
    if (orientacao_estimada == 'O'):
        virar_direita()
    while(sensor_cor.Color() == 'GREEN'):
        rodas.straight()
    dar_re_meio_bloco()
    virar_esquerda()
    while(sensor_cor.Color() == 'GREEN'):
        rodas.straight()
    dar_re_meio_bloco()
    virar_esquerda()
    virar_esquerda()

def cores_cacambas(cacambas, sensor_cor):
    alinhar_cacambas(sensor_cor_esq, orientacao_estimada)
    for i in range(len(cacambas)):
        if (i == 1):
            rodas.straight(dist_borda)
        rodas.straight(dist_cacamba + dist_borda)
        cacamba[i].cor = sensor_cor.Color()

def soltar_cacamba(cacambas, cor_cubo, hub):
    alinhar_cacambas(sensor_cor_esq, orientacao_estimada)
    for cacamba in cacamba:
        if cor_cubo == cacamba.cor:
            if(cacamba.cubo == 3):
                pass
            rodas.straight(cacamba.pos + cacamba.cubos*2*dist_cubo)
            virar_esquerda()
            abrir_garra(hub)
            cacamba.cubos += 1
            return