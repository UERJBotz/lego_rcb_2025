MAKEFLAGS += --jobs=2

PYTHON   = .venv/bin/python
PYBRICKS = .venv/bin/pybricksdev
AMPY     = .venv/bin/ampy

NOME_CABECA = "spike1"
NOME_BRACO  = "spike0"


.PHONY: all cabeca braco
all: cabeca braco

#! colocar os outros módulos como dependência
cabeca: cabeca.py
	$(PYBRICKS) run ble --name $(NOME_CABECA) $<
braco:  braco.py
	$(PYBRICKS) run ble --name $(NOME_BRACO) $<


.PHONY: imediato cabeca_imediato braco_imediato
imediato: cabeca braco

cabeca_imediato:
	$(PYTHON) build/run.py $(NOME_CABECA)
braco_imediato:
	$(PYTHON) build/run.py $(NOME_BRACO)


.PHONY: teste cabeca_teste braco_teste
teste: teste_cabeca teste_braco

TESTE_BRACO  = .__teste_braco__.py
TESTE_CABECA = .__teste_cabeca__.py

teste_cabeca: $(TESTE_CABECA)
	$(PYBRICKS) run ble --name $(NOME_CABECA) $<
teste_braco:  $(TESTE_BRACO)
	$(PYBRICKS) run ble --name $(NOME_BRACO) $<

$(TESTE_CABECA): cabeca.py
	echo "TESTE = True" > $@; cat $< >> $@
$(TESTE_BRACO): braco.py
	echo "TESTE = True" > $@; cat $< >> $@


.PHONY: rabo
#! ver algum jeito de não fazer upload sem precisar
# #! if grep -q $< <<<"$(AMPY) ls"; then echo "já tá" fi
# #! if ! "$(AMPY) get $<"; then echo "não tá" fi
#! colocar arduino-cli e fazer upload do arduino
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


.PHONY: clean
clean:
	rm -f $(TESTE_CABECA)
	rm -f $(TESTE_BRACO)

