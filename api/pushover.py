import requests

def enviar_mensaje(habitacion, cama):
    mensaje = f"📣 Llamada de asistencia en Habitación {habitacion}, Cama {cama}"
    enlace = f"http://localhost:5000/atender/{habitacion}/{cama}"

    data = {
        "token": "a8i8awj2manchfqs5fgh4odh3vxqwg",
        "user": "uuiv9azgxcn1ohssiqgck22o866uoc",
        "message": mensaje,
        "title": "Asistencia requerida",
        "priority": 2,
        "retry": 30,              # Reintentar cada 30s
        "expire": 180,            # Durante 3 minutos
        "url": enlace,
        "url_title": "✅ Atender solicitud de asistencia"
    }

    requests.post("https://api.pushover.net/1/messages.json", data=data)
