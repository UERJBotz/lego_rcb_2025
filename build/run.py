import asyncio
import sys

from pybricksdev.ble import find_device
from pybricksdev.connections.pybricks import PybricksHub

# https://github.com/orgs/pybricks/discussions/1159
async def main(nome=None, arquivo=None, wait="True", *args):
    try:
        print(f"Conectando a {nome}...")
        dev = await find_device(nome)
    except TimeoutError:
        print("Tempo excedido.")
        print("Verifique que o spike está ligado e tente novamente...")
        return

    hub = PybricksHub()
    await hub.connect(dev)
    await hub.run(arquivo, wait=eval(wait), print_output=True)
    await hub.disconnect()

_, *args = sys.argv
try:
    asyncio.run(main(*args))
except KeyboardInterrupt:
    print("Cancelado")
