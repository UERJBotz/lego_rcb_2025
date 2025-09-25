def inverte_caminho(caminho):
    inverso = caminho[::-1]
    for i in range(len(inverso)):
        dx, dy = inverso[i]
        inverso[i] = [-dx, -dy]
    return inverso

def procura(origem):
    cel_incertas = mapa.celulas_incertas()
    caminho_todo = []
    cel_inicio = origem

    #! ordenar lista com o a_estrela

    for cel_destino in celulas_incertas:
        caminho = a_estrela(cel_inicio, cel_destino)
        if not caminho: continue

        seguir_caminho(caminho)
        caminho_todo += caminho
        cel_inicio = cel_destino

        cor = ler_cor_cubo()
        if cor is None: # não tem cubo
            mapa.marcar_celula_livre(cel_destino)
            continue

        if not cor_nas_caçambas(cor): #!
            if cor == branco: tocar_musica(hub) #! fazer fora?
            mapa.marcar_celula_ocupada(cel_destino)
            dar_re_um_bloco()

            caminho_todo.pop(-1)
            cel_inicio = caminho_todo[-1]
            continue

        pegar_cubo()
        mapa.marcar_celula_livre(cel_destino)
        return cor, caminho_todo

    raise SucessoOuCatástrofe()
