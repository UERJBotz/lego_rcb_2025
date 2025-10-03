from pybricks.tools import wait

notas_derrota = ["G4/4_",
                 "F#4/4_",
                 "F4/4_", 
                 "E4/3"]

notas_vitoria = [     
                      "E3/4", "E3/4",
               "R/4",  
                      "E3/4", 
               "R/4",  
                      "C3/4", "E3/4", 
               "R/4",
                      "G3/4",
 "R/4", "R/4", "R/4",
                      "G3/4",
 "R/4", "R/4", "R/4",
                      "C4/4",
        "R/4", "R/4",
                      "G3/4",
        "R/4", "R/4",
                      "E3/4", 
        "R/4", "R/4",
                      "A4/4",
               "R/4",  
                      "B4/4",
               "R/4",  
                      "A#4/4", "A4/4",
               "R/4",
                      "G3/3", "E3/3", "G3/3", "A4/4",
               "R/4",  
                      "F3/4", "G3/4",
               "R/4",  
                      "E3/4", 
               "R/4",  
                      "C3/4",
]
#! melhorar musiquinha vitória (mario), talvez só cortar

bipe_inicio = lambda hub: hub.speaker.beep(frequency=500, duration=100)
bipe_final  = lambda hub: hub.speaker.beep(frequency=250, duration=250)

bipe_calibracao = lambda hub: hub.speaker.beep(frequency=300, duration=100)
bipe_separador  = lambda hub: hub.speaker.beep(frequency=600, duration=200)
bipe_cabeca     = lambda hub: hub.speaker.beep(frequency=600, duration=100)

bipe_falha      = lambda hub: (hub.speaker.beep(frequency=800, duration=500), 
                               wait(200),
                               hub.speaker.beep(frequency=800, duration=500))

musica_vitoria = lambda hub: hub.speaker.play_notes(notas_vitoria, tempo=220)
musica_derrota = lambda hub: hub.speaker.play_notes(notas_derrota) #! ajustar tempo, etc
