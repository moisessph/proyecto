import requests

def obtener_ip_rele(habitacion, cama):
    # Por ejemplo: rele 101 = 192.168.1.201
    return f"192.168.1.{100 + int(habitacion)}"

def encender_piloto(habitacion, cama):
    ip = obtener_ip_rele(habitacion, cama)
    try:
        requests.get(f"http://{ip}/relay/0?turn=on")
    except:
        print(f"⚠️ Error al encender el piloto de {habitacion}-{cama}")

def apagar_piloto(habitacion, cama):
    ip = obtener_ip_rele(habitacion, cama)
    try:
        requests.get(f"http://{ip}/relay/0?turn=off")
    except:
        print(f"⚠️ Error al apagar el piloto de {habitacion}-{cama}")
