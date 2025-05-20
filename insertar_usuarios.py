from api.db import insertar_usuario, crear_tabla_usuarios

# Crear tabla si no existe
crear_tabla_usuarios()

# Insertar asistentes
insertar_usuario("Laura", "abc123", "clave123")
insertar_usuario("Carlos", "def456", "clave456")
insertar_usuario("Ana", "ghi789", "clave789")

print("✅ Usuarios insertados correctamente.")
