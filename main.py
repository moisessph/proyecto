from flask import Flask, render_template, request, redirect, make_response, Response
from api.pushover import enviar_mensaje
from api.relay import encender_piloto, apagar_piloto
from api.db import registrar_llamada, registrar_presencia
import sqlite3
from datetime import datetime, timedelta
import csv

app = Flask(__name__, static_folder="web/static", template_folder="templates")

# ------------------------ LLAMADAS Y PRESENCIAS ------------------------

@app.route("/llamada/<habitacion>/<cama>")
def llamada(habitacion, cama):
    print(f"[LLAMADA] {habitacion}-{cama}")
    registrar_llamada(habitacion, cama)
    encender_piloto(habitacion, cama)
    enviar_mensaje(habitacion, cama)
    clave = f"estado_{habitacion}_{cama}"
    resp = make_response(render_template("confirmacion.html", habitacion=habitacion, cama=cama, tipo="llamada"))
    resp.set_cookie(clave, "llamada", max_age=300)
    return resp

@app.route("/presencia/<habitacion>/<cama>")
def presencia(habitacion, cama):
    print(f"[PRESENCIA] {habitacion}-{cama}")
    registrar_presencia(habitacion, cama)
    apagar_piloto(habitacion, cama)
    clave = f"estado_{habitacion}_{cama}"
    resp = make_response(render_template("confirmacion.html", habitacion=habitacion, cama=cama, tipo="presencia"))
    resp.set_cookie(clave, "presencia", max_age=300)
    return resp

# ------------------------ PANEL ------------------------

@app.route("/panel")
def panel_llamadas():
    codigo = request.cookies.get("asistente")
    nombre = None
    if codigo:
        conn = sqlite3.connect("api/paciente.db")
        cursor = conn.cursor()
        cursor.execute("SELECT nombre FROM usuarios WHERE codigo = ?", (codigo,))
        row = cursor.fetchone()
        if row:
            nombre = row[0]
        conn.close()
    habitaciones = [f"{100 + i}" for i in range(1, 6)]
    camas = ["a", "b"]
    return render_template("panel.html", habitaciones=habitaciones, camas=camas, nombre_asistente=nombre)

# ------------------------ LOGIN ------------------------

@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "GET":
        return render_template("login.html")
    else:
        nombre = request.form["nombre"]
        codigo = request.form["codigo"]
        contraseña = request.form["contraseña"]
        try:
            conn = sqlite3.connect("api/paciente.db")
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM usuarios WHERE codigo = ? AND contraseña = ?", (codigo, contraseña))
            usuario = cursor.fetchone()
            conn.close()
            if usuario:
                resp = make_response(redirect("/panel"))
                resp.set_cookie("asistente", codigo, max_age=3600)
                print(f"[LOGIN] Asistente '{codigo}' autenticado.")
                return resp
            else:
                return "❌ Credenciales incorrectas", 401
        except Exception as e:
            print(f"[LOGIN ERROR] {e}")
            return "Error interno", 500

# ------------------------ ENROLL ------------------------

@app.route("/enroll", methods=["GET", "POST"])
def enroll():
    if request.method == "GET":
        return render_template("enroll.html")
    else:
        codigo = request.form["codigo"].strip()
        try:
            conn = sqlite3.connect("api/paciente.db")
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM usuarios WHERE codigo = ?", (codigo,))
            usuario = cursor.fetchone()
            conn.close()
            if usuario:
                resp = make_response(redirect("/panel"))
                resp.set_cookie("asistente", codigo, max_age=8*3600)
                print(f"[ENROLL] Dispositivo vinculado al asistente: {codigo}")
                return resp
            else:
                return "❌ Código inválido o asistente no registrado.", 401
        except Exception as e:
            print(f"[ENROLL ERROR] {e}")
            return "Error interno", 500

# ------------------------ LOGOUT ------------------------

@app.route("/logout")
def logout():
    resp = make_response(redirect("/login"))
    resp.delete_cookie("asistente")
    print("[LOGOUT] Cookie de sesión eliminada.")
    return resp

# ------------------------ HISTÓRICO ------------------------

@app.route("/historico", methods=["GET"])
def mostrar_historico():
    tipo = request.args.get("tipo", "todos")
    habitacion = request.args.get("habitacion", "").strip()
    nombre_asistente = None
    codigo = request.cookies.get("asistente")
    if codigo:
        conn = sqlite3.connect("api/paciente.db")
        cursor = conn.cursor()
        cursor.execute("SELECT nombre FROM usuarios WHERE codigo = ?", (codigo,))
        row = cursor.fetchone()
        if row:
            nombre_asistente = row[0]
        conn.close()
    try:
        conn = sqlite3.connect("api/paciente.db")
        cursor = conn.cursor()
        sql = "SELECT habitacion, cama, fecha, tipo FROM llamadas"
        condiciones = []
        valores = []
        if tipo != "todos":
            condiciones.append("tipo = ?")
            valores.append(tipo)
        if habitacion:
            condiciones.append("habitacion = ?")
            valores.append(habitacion)
        if condiciones:
            sql += " WHERE " + " AND ".join(condiciones)
        sql += " ORDER BY fecha DESC"
        cursor.execute(sql, valores)
        registros = cursor.fetchall()
        return render_template("historico.html", registros=registros, filtro_tipo=tipo, filtro_habitacion=habitacion, nombre_asistente=nombre_asistente)
    except Exception as e:
        print(f"[ERROR HISTÓRICO] {e}")
        return render_template("historico.html", registros=[], filtro_tipo=tipo, filtro_habitacion=habitacion, nombre_asistente=nombre_asistente)
    finally:
        conn.close()

@app.route("/historico/borrar")
def borrar_historico():
    nombre_asistente = None
    codigo = request.cookies.get("asistente")
    if codigo:
        conn = sqlite3.connect("api/paciente.db")
        cursor = conn.cursor()
        cursor.execute("SELECT nombre FROM usuarios WHERE codigo = ?", (codigo,))
        row = cursor.fetchone()
        if row:
            nombre_asistente = row[0]
        conn.close()
    try:
        conn = sqlite3.connect("api/paciente.db")
        cursor = conn.cursor()
        cursor.execute("DELETE FROM llamadas")
        conn.commit()
        return render_template("historico.html", registros=[], filtro_tipo="todos", filtro_habitacion="", nombre_asistente=nombre_asistente)
    except Exception as e:
        print(f"[ERROR BORRADO] {e}")
        return render_template("historico.html", registros=[], filtro_tipo="todos", filtro_habitacion="", nombre_asistente=nombre_asistente)
    finally:
        conn.close()

# ------------------------ ASISTENCIAS ------------------------

@app.route("/asistencias")
def asistencias_turno():
    nombre_asistente = None
    codigo = request.cookies.get("asistente")
    if not codigo:
        return redirect("/login")

    try:
        conn = sqlite3.connect("api/paciente.db")
        cursor = conn.cursor()
        cursor.execute("SELECT nombre FROM usuarios WHERE codigo = ?", (codigo,))
        row = cursor.fetchone()
        if row:
            nombre_asistente = row[0]

        hace_24h = (datetime.now() - timedelta(hours=24)).strftime("%Y-%m-%d %H:%M:%S")
        cursor.execute("""
            SELECT habitacion, cama, fecha, tipo
            FROM llamadas
            WHERE fecha >= ?
            ORDER BY fecha DESC
        """, (hace_24h,))
        registros = cursor.fetchall()

        conn.close()
        return render_template("asistencias.html", registros=registros, nombre_asistente=nombre_asistente)

    except Exception as e:
        print(f"[ASISTENCIAS ERROR] {e}")
        return "Error cargando asistencias", 500

@app.route("/asistencias/exportar")
def exportar_asistencias_csv():
    try:
        conn = sqlite3.connect("api/paciente.db")
        cursor = conn.cursor()
        hace_24h = (datetime.now() - timedelta(hours=24)).strftime("%Y-%m-%d %H:%M:%S")

        cursor.execute("""
            SELECT habitacion, cama, fecha, tipo
            FROM llamadas
            WHERE fecha >= ?
            ORDER BY fecha DESC
        """, (hace_24h,))
        registros = cursor.fetchall()
        conn.close()

        def generar_csv():
            salida = csv.StringIO()
            writer = csv.writer(salida)
            writer.writerow(["Habitación", "Cama", "Fecha", "Tipo"])
            writer.writerows(registros)
            return salida.getvalue()

        return Response(
            generar_csv(),
            mimetype="text/csv",
            headers={"Content-Disposition": "attachment; filename=asistencias_turno.csv"}
        )

    except Exception as e:
        print(f"[EXPORT CSV ERROR] {e}")
        return "Error exportando CSV", 500
    
@app.route("/historico/exportar")
def exportar_historico_csv():
    try:
        conn = sqlite3.connect("api/paciente.db")
        cursor = conn.cursor()
        cursor.execute("""
            SELECT habitacion, cama, fecha, tipo
            FROM llamadas
            ORDER BY fecha DESC
        """)
        registros = cursor.fetchall()
        conn.close()

        def generar_csv():
            salida = csv.StringIO()
            writer = csv.writer(salida)
            writer.writerow(["Habitación", "Cama", "Fecha", "Tipo"])
            writer.writerows(registros)
            return salida.getvalue()

        return Response(
            generar_csv(),
            mimetype="text/csv",
            headers={"Content-Disposition": "attachment; filename=historico_completo.csv"}
        )

    except Exception as e:
        print(f"[EXPORT HISTORICO ERROR] {e}")
        return "Error exportando histórico", 500

# ------------------------ GESTIÓN DE ASISTENTES ------------------------

@app.route("/asistentes")
def ver_asistentes():
    codigo = request.cookies.get("asistente")
    nombre_asistente = None
    if not codigo:
        return redirect("/login")
    conn = sqlite3.connect("api/paciente.db")
    cursor = conn.cursor()
    cursor.execute("SELECT nombre FROM usuarios WHERE codigo = ?", (codigo,))
    row = cursor.fetchone()
    if row:
        nombre_asistente = row[0]
    cursor.execute("SELECT * FROM usuarios ORDER BY nombre")
    asistentes = cursor.fetchall()
    conn.close()
    return render_template("asistentes.html", asistentes=asistentes, nombre_asistente=nombre_asistente)

@app.route("/asistentes/crear", methods=["POST"])
def crear_asistente():
    nombre = request.form["nombre"]
    codigo = request.form["codigo"]
    contraseña = request.form["contraseña"]
    try:
        conn = sqlite3.connect("api/paciente.db")
        cursor = conn.cursor()
        cursor.execute("INSERT INTO usuarios (nombre, codigo, contraseña) VALUES (?, ?, ?)", (nombre, codigo, contraseña))
        conn.commit()
        conn.close()
        return redirect("/asistentes")
    except Exception as e:
        print(f"[CREAR ASISTENTE ERROR] {e}")
        return "Error al crear asistente", 500

@app.route("/asistentes/editar", methods=["POST"])
def editar_asistente():
    nombre = request.form["nombre"]
    codigo = request.form["codigo"]
    contraseña = request.form["contraseña"]
    try:
        conn = sqlite3.connect("api/paciente.db")
        cursor = conn.cursor()
        cursor.execute("UPDATE usuarios SET nombre = ?, contraseña = ? WHERE codigo = ?", (nombre, contraseña, codigo))
        conn.commit()
        conn.close()
        return redirect("/asistentes")
    except Exception as e:
        print(f"[EDITAR ASISTENTE ERROR] {e}")
        return "Error al editar asistente", 500

@app.route("/asistentes/eliminar", methods=["POST"])
def eliminar_asistente():
    codigo = request.form["codigo"]
    try:
        conn = sqlite3.connect("api/paciente.db")
        cursor = conn.cursor()
        cursor.execute("DELETE FROM usuarios WHERE codigo = ?", (codigo,))
        conn.commit()
        conn.close()
        return redirect("/asistentes")
    except Exception as e:
        print(f"[ELIMINAR ASISTENTE ERROR] {e}")
        return "Error al eliminar asistente", 500

@app.route("/reset/<habitacion>/<cama>")
def reset_estado(habitacion, cama):
    clave = f"estado_{habitacion}_{cama}"
    print(f"[RESET] Restableciendo estado de {habitacion}-{cama}")
    resp = make_response(redirect("/panel"))
    resp.set_cookie(clave, "", expires=0)
    return resp

# ------------------------ INICIO ------------------------

if __name__ == "__main__":
    app.run(debug=True)
