def rgb_to_hsv(rgb): # roubado de Lib/colorsys
    r, g, b = rgb
    maxc = max(r, g, b)
    minc = min(r, g, b)
    rangec = (maxc-minc)
    v = maxc
    if minc == maxc:
        return 0.0, 0.0, v
    s = rangec / maxc
    rc = (maxc-r) / rangec
    gc = (maxc-g) / rangec
    bc = (maxc-b) / rangec
    if r == maxc:
        h = bc-gc
    elif g == maxc:
        h = 2.0+rc-bc
    else:
        h = 4.0+gc-rc
    h = (h/6.0) % 1.0

    return (h, s, v)

def hsv_to_rgb(hsv): # roubado de Lib/colorsys
    h, s, v = hsv
    if s == 0.0:
        return v, v, v
    i = int(h*6.0) # XXX assume int() truncates!
    f = (h*6.0) - i
    p = v*(1.0 - s)
    q = v*(1.0 - s*f)
    t = v*(1.0 - s*(1.0-f))
    i = i%6
    if i == 0:
        return v, t, p
    if i == 1:
        return q, v, p
    if i == 2:
        return p, v, t
    if i == 3:
        return p, q, v
    if i == 4:
        return t, p, v
    if i == 5:
        return v, p, q
    # Cannot get here

class Enum():
    """
    A simple (and fallible) substitute for the enum.Enum class
    """
    def __init__(self, cls_name, items):
        if type(items) == dict:
            names = items.keys()
            vals  = items.values()
        else:
            names = items
            vals  = range(len(items))
        
        self.name_str_list = names
        self.constant_map = dict(zip(names, vals))
        self.name_str_map = dict(zip(vals, names))


    def __getattr__(self, name):
        return self.constant_map[name]
    
    def __getitem__(self, item):
        return self.constant_map[item]
    def __call__(self, num):
        return self.name_str_map[num]
    
    def __iter__(self):
        yield from self.name_str_list

    def __contains__(self, val):
        return (val in self.constant_map or
                val in self.name_str_map)

    def __len__(self):
        return len(self.constant_map)
    
    #! faltam esses, e talvez criar um tipo interno pra os elementos
    #! retornar esse tipo novo em vez dos números direto
    #def __repr__(self): pass
    #def __str__(self): pass


## testes

# cor = enum("cor", ["AMARELO",
#                    "VERDE",
#                    "CINZA",
#                    "PRETO",
#                    "BRANCO"])
# print(cor.VERDE, cor.PRETO, len(cor), "AMARELO" in cor, sep='\t')
# print(list(cor))
#
# from enum import Enum
# cor2 = Enum("cor2", ["AMARELO",
#                      "VERDE",
#                      "CINZA",
#                      "PRETO",
#                      "BRANCO"])
# print(cor2.VERDE, cor2.PRETO, len(cor2), "AMARELO" in cor2, sep='\t')
# print(list(cor2))