# Create_db.py
import pymysql 
from dotenv import load_dotenv
import os

def crear_base_y_tablas():
    load_dotenv()
    host = os.getenv("MYSQL_HOST")
    user = os.getenv("MYSQL_USER")
    password = os.getenv("MYSQL_PASSWORD")
    database = os.getenv("MYSQL_DATABASE")

    con = None # Inicializar con a None
    try:
        # Conectar sin especificar base de datos (por si aún no existe)
        print("Intentando conectar a MySQL para crear la base de datos...")
        con = pymysql.connect(host=host, user=user, password=password) # Usar pymysql aquí
        cursor = con.cursor()
        print("✅ Conexión exitosa a MySQL en crear_base_y_tablas.")

        # Crear la base de datos si no existe
        cursor.execute(f"CREATE DATABASE IF NOT EXISTS {database}")
        print(f"Base de datos '{database}' verificada/creada.")

        # Seleccionar la base de datos después de crearla (o si ya existía)
        cursor.execute(f"USE {database}") # <--- ¡Añadir esta línea!

        # Crear tabla usuarios
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS usuarios (
                id INT AUTO_INCREMENT PRIMARY KEY,
                nombre VARCHAR(100),
                correo VARCHAR(100) UNIQUE,
                contraseña VARCHAR(256),
                tipo VARCHAR(20),
                mi_lista TEXT,
                favoritas TEXT,
                historial_sesiones TEXT
            )
        """)
        print("Tabla 'usuarios' verificada/creada.")

        # Crear tabla visualizaciones
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS visualizaciones (
                id INT AUTO_INCREMENT PRIMARY KEY,
                correo VARCHAR(100),
                pelicula TEXT,
                cantidad INT DEFAULT 1,
                fecha DATETIME DEFAULT CURRENT_TIMESTAMP
            )
        """)
        print("Tabla 'visualizaciones' verificada/creada.")

        con.commit()
        print("Tablas creadas/verificadas y cambios guardados.")

    except pymysql.Error as err: # Cambiado a pymysql.Error
        print(f"❌ ¡ERROR DE MYSQL al crear la base de datos o tablas!: {err}")
        print(f"Detalles de conexión: Host={host}, User={user}, Database={database}")
    except Exception as e:
        print(f"❌ Ocurrió un ERROR INESPERADO en crear_base_y_tablas: {e}")
    finally:
        # La conexión con PyMySQL (y el cursor) se cierran si existe.
        # No hay un método is_connected() directo en PyMySQL como en mysql.connector.
        if con: # Simplemente verifica si la conexión existe
            cursor.close()
            con.close()
            print("Conexión a MySQL cerrada en crear_base_y_tablas.")

if __name__ == "__main__":
    crear_base_y_tablas()
