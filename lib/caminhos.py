from lib.polyfill import Enum, heappop, heappush

tipo_celula = Enum("tipo_celula", ["RUA",
                                   "CRUZ",
                                   "NADA",
                                   "SAFE"])

tipo_parede = Enum("tipo_parede", ["PAREDE",
                                   "ENTRADA"])

estado_celula = Enum("estado_celula", ["LIVRE",
                                       "OCUPADA",
                                       "INCERTO"])

posicao_parede = Enum("posicao_parede", ["N", "L", "S", "O"])

class Rua:
    def __init__(self):
        self.tipo = tipo_celula.RUA
        self.estado = estado_celula.INCERTO
    def __str__(self):
        return '*'

class Cruz:
    def __init__(self):
        self.tipo = tipo_celula.RUA
        self.estado = estado_celula.LIVRE
    def __str__(self):
        return '*'

class Safe:
    def __init__(self):
        self.tipo = tipo_celula.SAFE
        self.estado = estado_celula.LIVRE
    def __str__(self):
        return '#'

class Nada:
    def __init__(self):
        self.tipo = tipo_celula.NADA
        self.estado = estado_celula.OCUPADA
    def __str__(self):
        return ' '

# celula = Rua | Cruzamento | Safezone | Void

def imprime_matriz(matriz):
    """Imprime a matriz de forma alinhada."""
    largura_maxima = 12

    print(end='  ')
    for i in range(len(matriz[0])):
        print((f"{i}     ")[:2], end=' ')
    print()

    i = 0
    for linha in matriz:
        print(i, end=' ')
        i += 1

        for celula in linha:
            texto = str(celula)
            estado = 'X' if celula.estado == estado_celula.OCUPADA else (
                     '?' if celula.estado == estado_celula.INCERTO else texto)
            print(estado*2, end=" ")
        print()

#! ver se lambdar os outros também

def coloca_obstaculo(x, y):
    cel = mapa[y][x]
    if cel.tipo == tipo_celula.RUA: #! falhar mais alto
        cel.estado = estado_celula.OCUPADA

def tira_obstaculo(x, y):
    cel = mapa[y][x]
    if cel.tipo == tipo_celula.RUA:
        cel.estado = estado_celula.LIVRE

mapa = [
    [Safe(), Safe(), Cruz(),  Rua(), Cruz(),  Rua(), Cruz(),  Rua(), Cruz(),  Rua(), Cruz(),  Rua(), Cruz()],
    [Safe(), Nada(),  Rua(), Nada(),  Rua(), Nada(),  Rua(), Nada(),  Rua(), Nada(),  Rua(), Nada(),  Rua()],
    [Safe(), Safe(), Cruz(),  Rua(), Cruz(),  Rua(), Cruz(),  Rua(), Cruz(),  Rua(), Cruz(),  Rua(), Cruz()],
    [Safe(), Nada(),  Rua(), Nada(),  Rua(), Nada(),  Rua(), Nada(),  Rua(), Nada(),  Rua(), Nada(),  Rua()],
    [Safe(), Safe(), Cruz(),  Rua(), Cruz(),  Rua(), Cruz(),  Rua(), Cruz(),  Rua(), Cruz(),  Rua(), Cruz()],
    [Safe(), Nada(),  Rua(), Nada(),  Rua(), Nada(),  Rua(), Nada(),  Rua(), Nada(),  Rua(), Nada(),  Rua()],
    [Safe(), Safe(), Cruz(),  Rua(), Cruz(),  Rua(), Cruz(),  Rua(), Cruz(),  Rua(), Cruz(),  Rua(), Cruz()],
    [Safe(), Nada(),  Rua(), Nada(),  Rua(), Nada(),  Rua(), Nada(),  Rua(), Nada(),  Rua(), Nada(),  Rua()],
    [Safe(), Safe(), Cruz(),  Rua(), Cruz(),  Rua(), Cruz(),  Rua(), Cruz(),  Rua(), Cruz(),  Rua(), Cruz()]
]

## implementação do A* (adaptada de <https://www.geeksforgeeks.org/a-search-algorithm-in-python/>)
class Cell():
    def __init__(self, i_pai=0,
                       j_pai=0,
                       f=float('inf'),
                       g=float('inf'),
                       h=0):
        self.i_pai = i_pai # Parent cell's row index
        self.j_pai = j_pai # Parent cell's column index
        self.f     = f # Total cost of the cell (g + h)
        self.g     = g # Cost from start to this cell
        self.h     = h # Heuristic cost from this cell to destination

direcoes = [(0, 1), (1, 0), (0, -1), (-1, 0)]  # Movimentos: direita, baixo, esquerda, cima

def dist_manhatan(posicao_atual, destino):
    atual_x, atual_y = posicao_atual
    dest_x,  dest_y  = destino
    return abs(atual_x - dest_x) + abs(atual_y - dest_y)

def dentro_dos_limites(matriz, cell):
    row, col = cell
    return 0 <= row < len(matriz) and 0 <= col < len(matriz[0])

def celula_ocupada(grid, cell):
    row, col = cell
    return grid[row][col].estado == estado_celula.OCUPADA

def celula_livre(grid, cell):
    row, col = cell
    return grid[row][col].estado == estado_celula.LIVRE

#!
def eh_destino(src, dest):
    row, col = src
    return row == dest[0] and col == dest[1]

def heuristica(src, dest):
    return dist_manhatan(src, dest)

# Trace the path from source to destination
def tracar_caminho(info_celulas, dest):
    print("The Path is ")
    path = []
    row, col = dest

    # Trace the path from destination to source using parent cells
    while not (info_celulas[row][col].i_pai == row and info_celulas[row][col].j_pai == col):
        path.append((row, col))
        temp_row = info_celulas[row][col].i_pai
        temp_col = info_celulas[row][col].j_pai
        row = temp_row
        col = temp_col

    # Add the source cell to the path
    path.append((row, col))
    # Reverse the path to get the path from source to destination
    path.reverse()
    
    return path

# Implement the A* search algorithm
def a_estrela(grid, src, dest):
    ok = True
    if not dentro_dos_limites(grid, src):
        ok = False; print(f"a_estrela: origem inválida {src}")
    if not dentro_dos_limites(grid, dest):
        ok = False; print(f"a_estrela: destino inválido {dest}")

    if not celula_livre(grid, src):
        ok = False; print(f"a_estrela: origem bloqueada {src}")
    if celula_ocupada(grid, dest):
        ok = False; print(f"a_estrela: destino bloqueado {dest}")

    if not ok: return None

    # Check if we are already at the destination
    if eh_destino(src, dest):
        print(f"a_estrela: já no destino {src, dest}"); return []

    ROW = len(grid)
    COL = len(grid[0])

    # Initialize the closed list (visited cells)
    closed_list  = [[False for _ in range(COL)]  for _ in range(ROW)]
    # Initialize the details of each cell
    info_celulas = [[Cell() for _ in range(COL)] for _ in range(ROW)]

    # Initialize the start cell details
    i, j = src
    info_celulas[i][j] = Cell(f=0,
                              g=0,
                              h=0,
                              i_pai=i,
                              j_pai=j)

    # Initialize the open list (cells to be visited) with the start cell
    open_list = []
    heappush(open_list, (0.0, i, j))

    # Initialize the flag for whether destination is found
    achou_dest = False

    # Main loop of A* search algorithm
    while len(open_list) > 0:
        # Pop the cell with the smallest f value from the open list
        p = heappop(open_list)

        # Mark the cell as visited
        i = p[1]
        j = p[2]
        closed_list[i][j] = True

        # For each direction, check the successors
        for dir in direcoes:
            new_i = i + dir[0]
            new_j = j + dir[1]
            new = new_i, new_j

            # If the successor is valid, (unblocked or is destiny), and not visited
            if dentro_dos_limites(grid, new) and (celula_livre(grid, new) or eh_destino(new, dest)) and not closed_list[new_i][new_j]:
                # If the successor is the destination
                if eh_destino(new, dest):
                    # Set the parent of the destination cell
                    info_celulas[new_i][new_j].i_pai = i
                    info_celulas[new_i][new_j].j_pai = j
                    print("a_estrela: caminho encontrado")
                    # Trace and print the path from source to destination
                    return tracar_caminho(info_celulas, dest)
                else:
                    # Calculate the new f, g, and h values
                    g_new = info_celulas[i][j].g + 1.0
                    h_new = heuristica(new, dest)
                    f_new = g_new + h_new

                    # If the cell is not in the open list or the new f value is smaller
                    if info_celulas[new_i][new_j].f == float('inf') or info_celulas[new_i][new_j].f > f_new:
                        # Add the cell to the open list
                        heappush(open_list, (f_new, new_i, new_j))
                        # Update the cell details
                        info_celulas[new_i][new_j] = Cell(f = f_new,
                                                          g = g_new,
                                                          h = h_new,
                                                          i_pai = i,
                                                          j_pai = j)

    # If the destination is not found after visiting all cells
    if not achou_dest:
        print("a_estrela: não achou")

    return None

#funcao que recebe lista de posicoes na matriz e transforma em lista de direcoes
def caminho_relativo(caminho_absoluto: list[tuple[int, int]]):
    if caminho_absoluto is None:
        caminho_absoluto = []
        print("Caminho Errado")

    #movimentos
    direita = (0, 1); baixo = (1, 0); esquerda = (0, -1); cima = (-1, 0)
    direcoes = [(0,0)]

    # print(caminho_absoluto)
    for i in range(1, len(caminho_absoluto)):
        dx = caminho_absoluto[i][0] - caminho_absoluto[i - 1][0]
        dy = caminho_absoluto[i][1] - caminho_absoluto[i - 1][1]

        if   dx == 0 and dy == 1:
            direcoes.append(direita)
        elif dx == 1 and dy == 0:
            direcoes.append(baixo)
        elif dx == 0 and dy == -1:
            direcoes.append(esquerda)
        elif dx == -1 and dy == 0:
            direcoes.append(cima)

    return direcoes #! checar no chamador se é vazio

tipo_movimento = Enum("tipo_movimento",
                      ["FRENTE", "DIREITA_FRENTE", "ESQUERDA_FRENTE", "TRAS", "DIREITA", "ESQUERDA"])

def prox_movimento(ori_ini: tipo_movimento, ori_final: tipo_movimento): #type: ignore
        diferenca = (ori_final - ori_ini) % 4
        if   diferenca == 0: return tipo_movimento.FRENTE
        elif diferenca == 1: return tipo_movimento.DIREITA_FRENTE
        elif diferenca == 2: return tipo_movimento.TRAS
        elif diferenca == 3: return tipo_movimento.ESQUERDA_FRENTE
        else:
            assert False

def movimento_relativo(cam_rel, orientacao_ini):
    idx_orientacao = posicao_parede[orientacao_ini]
    nova_orientacao = orientacao_ini

    caminho_relativo = cam_rel.copy()
    caminho_relativo.pop(0)

    movimentos = []
    for movimento in caminho_relativo:
        if   movimento == ( 0, 1): nova_orientacao = "L"
        elif movimento == ( 1, 0): nova_orientacao = "S"
        elif movimento == ( 0,-1): nova_orientacao = "O"
        elif movimento == (-1, 0): nova_orientacao = "N"

        nova_idx_orientacao = posicao_parede[nova_orientacao]

        movimentos.append(
            prox_movimento(idx_orientacao, nova_idx_orientacao)
        )

        idx_orientacao = nova_idx_orientacao

    return movimentos, posicao_parede(idx_orientacao)


def achar_movimentos(pos_ini, pos_fim, orientacao):
    pos_ini = pos_ini[1], pos_ini[0]
    pos_fim = pos_fim[1], pos_fim[0]
    caminho = a_estrela(mapa, pos_ini, pos_fim)
    print("achar_movimentos:", *caminho, sep=" -> ")
    caminho_rel = caminho_relativo(caminho)
    print(f"achar_movimentos: {caminho_rel=}")

    movimentos, ori_fim = movimento_relativo(caminho_rel, orientacao)
    print(orientacao, [tipo_movimento(i) for i in movimentos], ori_fim)
    return movimentos, ori_fim

