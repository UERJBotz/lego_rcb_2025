# from https://pythonforundergradengineers.com/upload-py-files-to-esp8266-running-micropython.html

import esp; esp.osdebug(None) # disable esp osdebug
import uos, machine; uos.dupterm(None, 0) # disable REPL on UART(0)
#import webrepl; webrepl.start()

import gc; gc.collect()
