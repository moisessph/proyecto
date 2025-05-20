import sqlite3

conn = sqlite3.connect("api/paciente.db")
cursor = conn.cursor()

cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
tablas = cursor.fetchall()

print("Tablas existentes en la base de datos:")
for t in tablas:
    print("-", t[0])

conn.close()
