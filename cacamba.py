class Cacamba:
    def __init__(self):
        self.cor
        self.pos
        self.cubos

#dist_borda = x
#dist_sensor = y
dist_cacamba = 160
dist_cubo = 50

def vetor_cacambas():
    cacambas = []
    for i in range(6):
        new_cacamba = Cacamba()
        new_cacamba.pos = i+1 # dist_cacamba*i + dist_borda*(i+1) - dist_sensor
        new_cacamba.cubos = 0
        cacambas.append(new_cacamba)
    return cacambas

#começar da linha ate dist cacamba i - dist traseira ate sensor
def cores_cacambas(cacambas, sensor_cor):
    for cacamba in cacamba:
        #1 e dist_borda
        rodas.straight(cacamba.pos)#dist_cacamba + dist_borda
        cacamba.cor = sensor_cor.Color()

def soltar_cacamba(cacambas, cor_cubo, hub):
    for cacamba in cacamba:
        if cor_cubo == cacamba.cor:
            rodas.straight(cacamba.pos + cacamba.cubos)#cacamba.cubos*dist
            virar_direita()
            abrir_garra(hub)
            return