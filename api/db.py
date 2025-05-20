import sqlite3
from datetime import datetime

def conectar():
    return sqlite3.connect("api/paciente.db")

# ---------------------- LLAMADAS Y PRESENCIAS ----------------------

def registrar_llamada(habitacion, cama):
    print(f"[DB] Insertando llamada de {habitacion}-{cama}")
    conn = conectar()
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS llamadas (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            habitacion TEXT,
            cama TEXT,
            fecha TEXT,
            tipo TEXT
        )
    ''')
    fecha = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    cursor.execute("INSERT INTO llamadas (habitacion, cama, fecha, tipo) VALUES (?, ?, ?, ?)",
                   (habitacion, cama, fecha, "llamada"))
    conn.commit()
    conn.close()

def registrar_presencia(habitacion, cama):
    print(f"[DB] Insertando presencia en {habitacion}-{cama}")
    conn = conectar()
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS llamadas (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            habitacion TEXT,
            cama TEXT,
            fecha TEXT,
            tipo TEXT
        )
    ''')
    fecha = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    cursor.execute("INSERT INTO llamadas (habitacion, cama, fecha, tipo) VALUES (?, ?, ?, ?)",
                   (habitacion, cama, fecha, "presencia"))
    conn.commit()
    conn.close()

# ---------------------- USUARIOS (ASISTENTES) ----------------------

def crear_tabla_usuarios():
    conn = conectar()
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS usuarios (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            nombre TEXT NOT NULL,
            codigo TEXT UNIQUE NOT NULL,
            contraseña TEXT NOT NULL
        )
    ''')
    conn.commit()
    conn.close()

def insertar_usuario(nombre, codigo, contraseña):
    conn = conectar()
    cursor = conn.cursor()
    cursor.execute("INSERT INTO usuarios (nombre, codigo, contraseña) VALUES (?, ?, ?)",
                   (nombre, codigo, contraseña))
    conn.commit()
    conn.close()
