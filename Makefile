MAKEFLAGS += --jobs=2

PYTHON   = .venv/bin/python
PYBRICKS = .venv/bin/pybricksdev
AMPY     = .venv/bin/ampy

_BRACO  = .__main_braco__.py
_CABECA = .__main_cabeca__.py

NOME_CABECA = "spike1"
NOME_BRACO  = "spike0"


.PHONY:
all:: cabeca braco
all:: clean

.PHONY: cabeca braco
cabeca: $(_CABECA)
	$(PYBRICKS) run ble --name $(NOME_CABECA) $<
braco:  $(_BRACO)
	$(PYBRICKS) run ble --name $(NOME_BRACO) $<


.PHONY: cabeca_imediato braco_imediato
cabeca_imediato:
	$(PYTHON) build/run.py $(NOME_CABECA)
braco_imediato:
	$(PYTHON) build/run.py $(NOME_BRACO)


#! colocar os outros módulos como dependência
$(_CABECA): build/pre_cabeca.py main.py
	cat build/pre_cabeca.py main.py > $@

#! colocar os outros módulos como dependência
$(_BRACO): build/pre_braco.py main.py
	cat build/pre_braco.py main.py > $@

#! ver algum jeito de não fazer upload sem precisar
##! if grep -q $< <<<"$(AMPY) ls"; then echo "já tá" fi
##! if ! "$(AMPY) get $<"; then echo "não tá" fi
rabo:: firmware/rabo/boot.py
	$(AMPY) --port /dev/ttyACM0 put $<
rabo:: firmware/rabo/main.py
	$(AMPY) --port /dev/ttyACM0 put $<
rabo:: firmware/rabo/bleradio.py
	$(AMPY) --port /dev/ttyACM0 put $<
rabo:: lib/polyfill.py
	$(AMPY) --port /dev/ttyACM0 put $< $<
rabo:: bluetooth.py
	$(AMPY) --port /dev/ttyACM0 put $< blt.py


.PHONY:
clean:
	-rm $(_CABECA)
	-rm $(_BRACO)

