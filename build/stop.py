import asyncio
from pybricksdev.ble import find_device, BLERequestsConnection
from pybricksdev.ble.pybricks import Command

async def stop_user_program(nome=None, *args):
    try:
        print(f"Conectando a {nome}...")
        dev = await find_device(nome)
    except TimeoutError:
        print("Tempo excedido. Nenhum hub encontrado")
        return

    print("Falando com o hub")
    async with BLERequestsConnection(dev) as conn:
        try:
            await conn.command(Command.STOP_USER_PROGRAM)
            print("Commando de parada enviado")
        except Exception as e:
            print("Erro ao parar programa:", e)

if __name__ == "__main__":
    asyncio.run(stop_user_program())

