import os
import json
import hashlib
import pandas as pd
import logging
import pymysql as ms
import pymysql.cursors
from dotenv import load_dotenv

# -------------- Clase SQL -------------------
class GestorSQL:
    def __init__(self):
        try:
            print("🚀 Conectando a MySQL desde GestorSQL...")
            load_dotenv()
            host = os.getenv("MYSQL_HOST")
            user = os.getenv("MYSQL_USER")
            password = os.getenv("MYSQL_PASSWORD")
            database = os.getenv("MYSQL_DATABASE")

            print(f"DEBUG - Host: {host}")
            print(f"DEBUG - User: {user}")
            # print(f"DEBUG - Password: {password}") # No recomendable imprimir passwords en logs de producción
            print(f"DEBUG - Database: {database}")

            self.con = ms.connect(
                host=host,
                user=user,
                password=password,
                database=database
            )
            print("✅ Conexión MySQL exitosa")
            self.cursor = self.con.cursor(pymysql.cursors.DictCursor)
        except ms.Error as err:
            print(f"❌ ERROR ESPECÍFICO DE MYSQL en GestorSQL: {err}")
            raise # Re-lanza la excepción para que pueda ser capturada por el código que llamó a GestorSQL
        except Exception as e:
            print(f"❌ ERROR INESPERADO en GestorSQL: {e}")
            raise # Re-lanza la excepción

    def guardar_usuario(self, usuario: dict, tipo="normal"):
        self.cursor.execute("""
            INSERT INTO usuarios (nombre, correo, contraseña, tipo, mi_lista, favoritas, historial_sesiones)
            VALUES (%s, %s, %s, %s, %s, %s, %s)
            ON DUPLICATE KEY UPDATE
                nombre=VALUES(nombre),
                contraseña=VALUES(contraseña),
                tipo=VALUES(tipo),
                mi_lista=VALUES(mi_lista),
                favoritas=VALUES(favoritas),
                historial_sesiones=VALUES(historial_sesiones)
        """, (
            usuario["nombre"], usuario["correo"], usuario["contraseña"], tipo,
            json.dumps(usuario.get("mi_lista", [])),
            json.dumps(usuario.get("favoritas", [])),
            json.dumps(usuario.get("historial_sesiones", []))
        ))
        self.con.commit()

    def cargar_usuarios(self, tipo="normal"):
        self.cursor.execute("SELECT * FROM usuarios WHERE tipo=%s", (tipo,))
        datos = self.cursor.fetchall()
        usuarios = {}
        for row in datos:
            usuarios[row["correo"]] = {
                "nombre": row["nombre"],
                "contraseña": row["contraseña"],
                "mi_lista": json.loads(row["mi_lista"] or "[]"),
                "favoritas": json.loads(row["favoritas"] or "[]"),
                "historial_sesiones": json.loads(row["historial_sesiones"] or "[]")
            }
        return usuarios

    def registrar_visualizacion(self, correo_usuario, pelicula_id, pelicula_titulo):
        """
        Registra o actualiza la visualización de una película por un usuario.
        Si la película ya ha sido vista por el usuario, incrementa la cantidad.
        Si no, inserta un nuevo registro.
        """
        try:
            # Buscar si ya existe una visualización para esta película y usuario
            self.cursor.execute("""
                SELECT cantidad FROM visualizaciones
                WHERE correo = %s AND pelicula = %s
            """, (correo_usuario, pelicula_id)) # Se usa el ID de la película para asegurar unicidad
            resultado = self.cursor.fetchone()

            if resultado:
                # Si ya existe, actualiza la cantidad y la fecha
                nueva_cantidad = resultado['cantidad'] + 1
                self.cursor.execute("""
                    UPDATE visualizaciones
                    SET cantidad = %s, fecha = CURRENT_TIMESTAMP
                    WHERE correo = %s AND pelicula = %s
                """, (nueva_cantidad, correo_usuario, pelicula_id))
            else:
                # Si no existe, inserta una nueva visualización
                self.cursor.execute("""
                    INSERT INTO visualizaciones (correo, pelicula, cantidad)
                    VALUES (%s, %s, %s)
                """, (correo_usuario, pelicula_id, 1)) # Guardar el ID de la película
            self.con.commit()
            print(f"✅ Visualización registrada/actualizada para {correo_usuario} - {pelicula_titulo}")
            return True
        except ms.Error as err:
            print(f"❌ ERROR de MySQL al registrar visualización: {err}")
            return False
        except Exception as e:
            print(f"❌ ERROR INESPERADO al registrar visualización: {e}")
            return False

    def obtener_visualizaciones_usuario(self, correo_usuario):
        """
        Obtiene todas las visualizaciones de un usuario específico.
        Devuelve una lista de diccionarios con 'pelicula' (ID) y 'cantidad'.
        """
        try:
            self.cursor.execute("""
                SELECT pelicula, cantidad FROM visualizaciones
                WHERE correo = %s
                ORDER BY fecha DESC
            """, (correo_usuario,))
            return self.cursor.fetchall() # Esto devolverá una lista de diccionarios (pelicula, cantidad)
        except ms.Error as err:
            print(f"❌ ERROR de MySQL al obtener visualizaciones de usuario: {err}")
            return []
        except Exception as e:
            print(f"❌ ERROR INESPERADO al obtener visualizaciones de usuario: {e}")
            return []

    def obtener_visualizaciones_generales(self):
        """
        Obtiene el total de visualizaciones para cada película en general.
        Devuelve una lista de diccionarios con 'pelicula' (ID) y 'total_cantidad'.
        """
        try:
            self.cursor.execute("""
                SELECT pelicula, SUM(cantidad) AS total_cantidad FROM visualizaciones
                GROUP BY pelicula
                ORDER BY total_cantidad DESC
            """)
            return self.cursor.fetchall() # Lista de diccionarios (pelicula, total_cantidad)
        except ms.Error as err:
            print(f"❌ ERROR de MySQL al obtener visualizaciones generales: {err}")
            return []
        except Exception as e:
            print(f"❌ ERROR INESPERADO al obtener visualizaciones generales: {e}")
            return []

# ------------------ Clase Funciones Independientes -------------------
class Funciones:
    # Ahora, el gestor se inicializará solo cuando sea necesario
    _gestor_instance = None # Variable privada para la instancia perezosa

    @staticmethod
    def _get_gestor():
        """Obtiene la instancia de GestorSQL, creándola si aún no existe."""
        if Funciones._gestor_instance is None:
            Funciones._gestor_instance = GestorSQL()
        return Funciones._gestor_instance

    @staticmethod
    def _hash_contraseña(contraseña):
        """Hashea la contraseña usando SHA256."""
        return hashlib.sha256(contraseña.encode('utf-8')).hexdigest()

    @staticmethod
    def cargar_usuarios(tipo="normal"):
        return Funciones._get_gestor().cargar_usuarios(tipo) # Usa el método auxiliar

    @staticmethod
    def guardar_usuarios(usuarios, tipo="normal"):
        gestor = Funciones._get_gestor() # Obtiene la instancia del gestor
        for usuario in usuarios.values():
            gestor.guardar_usuario(usuario, tipo)

    @staticmethod
    def registrar_visualizacion(correo, pelicula):
        nombre_pelicula = pelicula if isinstance(pelicula, str) else pelicula.titulo.strip()
        fecha_pelicula = "Desconocido" if isinstance(pelicula, str) else str(pelicula.año).strip()
        clave_pelicula = f"{nombre_pelicula} ({fecha_pelicula})"
        Funciones._get_gestor().registrar_visualizacion(correo, clave_pelicula)

    @staticmethod
    def cargar_peliculas_desde_csv(ruta_csv):
        """Carga películas desde un archivo CSV."""
        if not os.path.exists(ruta_csv):
            raise FileNotFoundError(f"El archivo '{ruta_csv}' no existe.")

        df = pd.read_csv(ruta_csv)
        Columnas_de_cada_pelicula = {"names": "nombres", "date_x": "date", "score": "# score", "genre": "genero"}

        for col, alt in Columnas_de_cada_pelicula.items():
            if col not in df.columns:
                if alt in df.columns:
                    df.rename(columns={alt: col}, inplace=True)
                else:
                    raise ValueError(f"No se pudo cargar el CSV, falta la columna {col}.")
        return [Pelicula(idx, datos["names"], datos["date_x"], datos["score"], datos["genre"]) for idx, (_, datos) in enumerate(df.iterrows())]

    @staticmethod
    def cargar_peliculas_premium(ruta_csv):
        if not os.path.exists(ruta_csv):
            raise FileNotFoundError(f"El archivo '{ruta_csv}' no existe.")

        df = pd.read_csv(ruta_csv)
        df.columns = df.columns.str.strip() # Eliminar espacios en blanco en los nombres de las columnas

        Columnas_de_cada_pelicula = {"names": "nombres", "date_x": "date", "score": "# score", "genre": "genero"}

        for col, alt in Columnas_de_cada_pelicula.items():
            if col not in df.columns:
                if alt in df.columns:
                    df.rename(columns={alt: col}, inplace=True)
                else:
                    raise ValueError(f"No se pudo cargar el CSV, falta la columna {col}.")
        return [Pelicula(idx, datos["names"], datos["date_x"], datos["score"], datos["genre"]) for idx, (_, datos) in enumerate(df.iterrows())]

    @staticmethod
    def logger(nombre_logger: str, ruta_log: str, nivel=logging.DEBUG) -> logging.Logger:
        """
        Crea un logger con nombre único que escribe en la ruta especificada.

        Args: nombre_logger (str): Nombre del logger (por ejemplo, 'premium', 'cliente', etc.).
        ruta_log (str): Ruta completa al archivo de log (por ejemplo, 'Logs/errores.log').
        nivel (int): Nivel de logging (por defecto DEBUG).

        Returns:
        logging.Logger: Instancia del logger configurado.

        """
        # Asegurar que la carpeta del archivo exista
        os.makedirs(os.path.dirname(ruta_log), exist_ok=True)

        logger = logging.getLogger(nombre_logger)
        logger.setLevel(nivel)

        # Evitar duplicados: solo agrega handler si no lo tiene
        if not any(isinstance(h, logging.FileHandler) and h.baseFilename == os.path.abspath(ruta_log)
                   for h in logger.handlers):
            handler = logging.FileHandler(ruta_log, mode='w', encoding='utf-8')
            formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
            handler.setFormatter(formatter)
            logger.addHandler(handler)
        return logger

# ------------------- Clase  -------------------
class Pelicula:
    def __init__(self, id_pelicula, titulo, año=None, puntaje=None, genero=""):
        self.id_pelicula = id_pelicula
        self.titulo = titulo
        self.año = año if año else "Desconocido"
        self.puntaje = puntaje if puntaje else "N/A"
        self.genero = genero if genero else "Sin género"

    def __str__(self):
        return f"[{self.id_pelicula}] {self.titulo} - ({self.año}) - {self.puntaje} - {self.genero}"

class Catalogo:
    def __init__(self, peliculas):
        self.peliculas = sorted(peliculas, key=lambda p: p.titulo)

    def buscar(self, termino):
        """Busca películas por término y muestra índice junto a la información."""
        return [f"[{p.id_pelicula}] {p.titulo} ({p.año}) - {p.puntaje} - {p.genero}"
                for p in self.peliculas if termino.lower() in p.titulo.lower()]

    def recomendar(self, cantidad=15):
        """Recomienda películas basándose en el puntaje más alto y devuelve objetos `Pelicula`."""
        peliculas_ordenadas = sorted(
            self.peliculas,
            key=lambda p: float(str(p.puntaje).replace('.', '', 1)) if str(p.puntaje).replace('.', '', 1).isdigit() else 0,
            reverse=True
        )

        return peliculas_ordenadas[:cantidad]  # Devuelve los objetos "Pelicula", no texto.

class Usuario:
    def __init__(self, nombre, contraseña, correo):
        self.nombre = nombre
        self.contraseña_sin_hash = contraseña  # Guarda la contraseña sin hash temporalmente para verificación/hash
        # CAMBIO AQUÍ: Llamar a Funciones.hash_contraseña
        self.contraseña = Funciones._hash_contraseña(contraseña) # Almacena la contraseña ya hasheada
        self.correo = correo
        self.mi_lista = []
        self.favoritas = []
        self.historial_sesiones = []
        self.tipo = "normal"

    def iniciar_sesion(self, usuarios):
        # 'usuarios' aquí es el diccionario que Funciones.cargar_usuarios() devuelve desde la DB.
        # Contiene todos los datos (nombre, correo, contraseña, tipo, mi_lista, favoritas, historial_sesiones)
        
        datos_usuario_cargado = usuarios.get(self.correo) # Obtener los datos completos del usuario desde la DB

        if datos_usuario_cargado:
            # Verificar la contraseña
            contraseña_hasheada_almacenada = datos_usuario_cargado.get("contraseña")
            if not contraseña_hasheada_almacenada: # Manejar caso donde no hay contraseña almacenada
                return False, "Error: Contraseña no almacenada para este usuario."

            if self.verificar_contraseña(self.contraseña_sin_hash, contraseña_hasheada_almacenada):
                # Si el inicio de sesión es exitoso, actualiza el objeto Usuario (self)
                # con los datos completos cargados de la base de datos.
                self.nombre = datos_usuario_cargado.get("nombre", self.nombre)
                self.contraseña = contraseña_hasheada_almacenada # Usar la contraseña hasheada almacenada
                self.tipo = datos_usuario_cargado.get("tipo", "normal") # Cargar el tipo de usuario
                
                # Cargar listas y historial, asegurándose de que sean listas y no strings JSON
                # Se añade una comprobación para ver si el dato es un string (JSON) antes de intentar decodificar
                self.mi_lista = json.loads(datos_usuario_cargado.get("mi_lista", "[]")) if isinstance(datos_usuario_cargado.get("mi_lista"), str) else datos_usuario_cargado.get("mi_lista", [])
                self.favoritas = json.loads(datos_usuario_cargado.get("favoritas", "[]")) if isinstance(datos_usuario_cargado.get("favoritas"), str) else datos_usuario_cargado.get("favoritas", [])
                self.historial_sesiones = json.loads(datos_usuario_cargado.get("historial_sesiones", "[]")) if isinstance(datos_usuario_cargado.get("historial_sesiones"), str) else datos_usuario_cargado.get("historial_sesiones", [])

                return True, "Inicio de sesión exitoso."
            else:
                return False, "❌ Contraseña incorrecta."
        else:
            return False, "❌ Usuario no encontrado."
    
    def verificar_contraseña(self, contraseña_sin_hash, contraseña_hasheada_almacenada):
        """Verifica si la contraseña sin hash coincide con la contraseña hasheada."""
        # CAMBIO AQUÍ: Llamar a Funciones.hash_contraseña
        return Funciones._hash_contraseña(contraseña_sin_hash) == contraseña_hasheada_almacenada

    def registrar_usuario(self, usuarios, tipo="normal", duracion=0):
        """Registra un nuevo usuario en el sistema, asegurando que no esté duplicado en ambos archivos."""

        self.historial_sesiones = []
        if duracion and duracion > 0:
            self.historial_sesiones.append(duracion)

        # Eliminar de archivo del otro tipo
        otro_tipo = "premium" if tipo == "normal" else "normal"
        usuarios_otro = Funciones.cargar_usuarios(tipo=otro_tipo)
        if self.correo in usuarios_otro:
            del usuarios_otro[self.correo]
            Funciones.guardar_usuarios(usuarios_otro, tipo=otro_tipo)

        if self.correo in usuarios:
            return False, "El correo ya está registrado."

        usuarios[self.correo] = {
            "nombre": self.nombre,
            "correo": self.correo,
            "contraseña": self.contraseña,
            "mi_lista": [],
            "favoritas": [],
            "historial_sesiones": getattr(self, "historial_sesiones", [])
        }
        Funciones.guardar_usuarios(usuarios, tipo=tipo)
        return True, "¡Registro exitoso!"

    def recuperar_contraseña(self, usuarios, nueva_contraseña, tipo="normal"):
        """Permite actualizar la contraseña del usuario."""
        if self.correo not in usuarios:
            return False, "El correo no se encuentra registrado."

        usuarios[self.correo]["contraseña"] = Funciones.cifrar_contraseña(nueva_contraseña)
        Funciones.guardar_usuarios(usuarios, tipo=tipo)
        return True, "Contraseña actualizada exitosamente."

    def registrar_sesion(self, segundos):
        """Agrega la duración de una sesión al historial."""
        if not hasattr(self, "historial_sesiones"):
            self.historial_sesiones = []
        self.historial_sesiones.append(segundos)

class SistemaCineXtreem:
    def __init__(self, ruta_csv, peliculas=None, tipo_usuarios="normal"):
        self.tipo_usuarios = tipo_usuarios
        self.db = GestorSQL() # Esta es la primera instancia de GestorSQL que debería crearse
        self.usuarios = self.db.cargar_usuarios(tipo=tipo_usuarios) # Esto ahora usará Funciones._get_gestor()

        if peliculas is None:
            self.catalogo = Catalogo(Funciones.cargar_peliculas_desde_csv(ruta_csv))
        else:
            self.catalogo = Catalogo(peliculas)
        self.usuario_actual = None

    def poner_usuario_actual(self, usuario):
        """Asigna el usuario autenticado al sistema."""
        self.usuario_actual = usuario

    def ver_recomendaciones(self):
        return self.catalogo.recomendar()

    def buscar_pelicula(self, texto):
        texto = texto.lower().strip()

        # Filtrar películas y devolver los objetos reales, no texo
        # Además, permite busqueda por ID de pelicula
        resultados = [
            p for p in self.catalogo.peliculas
            if texto in p.titulo.lower() or texto == str(p.id_pelicula)
        ]
        return resultados  # Devuelve objetos "Pelicula", no cadenas.

    def ver_perfil(self):
        if self.usuario_actual:
            return {"nombre": self.usuario_actual.nombre, "correo": self.usuario_actual.correo}
        return None

    def agregar_a_lista(self, id_pelicula):
        """Agrega película a 'Ver más tarde' usando su ID real."""

        if not self.usuario_actual:
            return False, "⚠ Debes iniciar sesión primero."

        peli = next((p for p in self.catalogo.peliculas if p.id_pelicula == id_pelicula), None)

        if not peli:
            return False, "⚠ Película no encontrada."

        entrada = f"{peli.id_pelicula} | {peli.titulo} ({peli.año})"

        if entrada in self.usuario_actual.mi_lista:
            return False, "⚠ Ya está en tu lista de 'Ver más tarde'."

        self.usuario_actual.mi_lista.append(entrada)

        # Aseguramos que el diccionario completo para el usuario actual en self.usuarios
        # refleje todos los atributos del objeto 'usuario_actual' actualizado.
        correo_actual = self.usuario_actual.correo
        self.usuarios[correo_actual] = {
            "nombre": self.usuario_actual.nombre,
            "correo": self.usuario_actual.correo,
            "contraseña": self.usuario_actual.contraseña,
            "tipo": getattr(self.usuario_actual, 'tipo', "normal"), # Usa getattr para 'tipo' por seguridad
            "mi_lista": self.usuario_actual.mi_lista, # Esta es la lista que acabamos de actualizar
            "favoritas": self.usuario_actual.favoritas, # Aseguramos que otras listas también se copien
            "historial_sesiones": self.usuario_actual.historial_sesiones, # Y el historial de sesiones
        }
        Funciones.guardar_usuarios(self.usuarios, tipo=self.tipo_usuarios)
        return True, f"📌 '{entrada}' agregada a 'Ver más tarde'."

    def ver_mi_lista(self):
        if not self.usuario_actual:
            return False, ["⚠ Debes iniciar sesión primero."]

        lista = self.usuario_actual.mi_lista

        if not lista:
            return True, ["⚠ Tu lista de 'Ver más tarde' está vacía."]
        return True, lista

    def ver_favoritas(self):
        if not self.usuario_actual:
            return False, "⚠ Debes iniciar sesión primero."

        favoritas = self.usuario_actual.favoritas

        if not favoritas:
            return True, ["⚠ No has marcado ninguna película como favorita."]

        return True, favoritas  # Devuelve la lista correctamente

    def marcar_como_favorita(self, id_pelicula):
        """Marca una película como favorita usando su ID real."""

        if not self.usuario_actual:
            return False, "⚠ Debes iniciar sesión primero."

        # Busca la película con el ID correcto
        peli = next((p for p in self.catalogo.peliculas if p.id_pelicula == id_pelicula), None)

        if not peli:
            return False, "⚠ Película no encontrada."

        entrada = f"{peli.id_pelicula} | {peli.titulo} ({peli.año})"
        if entrada in self.usuario_actual.favoritas:
            return False, "⚠ Ya marcada como favorita."

        self.usuario_actual.favoritas.append(entrada)
        # Aseguramos que el diccionario completo para el usuario actual en self.usuarios
        # refleje todos los atributos del objeto 'usuario_actual' actualizado.
        correo_actual = self.usuario_actual.correo
        self.usuarios[correo_actual] = {
            "nombre": self.usuario_actual.nombre,
            "correo": self.usuario_actual.correo,
            "contraseña": self.usuario_actual.contraseña,
            "tipo": getattr(self.usuario_actual, 'tipo', "normal"), # Usa getattr para 'tipo' por seguridad
            "mi_lista": self.usuario_actual.mi_lista, # Esta es la lista que acabamos de actualizar
            "favoritas": self.usuario_actual.favoritas, # Aseguramos que otras listas también se copien
            "historial_sesiones": self.usuario_actual.historial_sesiones, # Y el historial de sesiones
        }
        Funciones.guardar_usuarios(self.usuarios, tipo=self.tipo_usuarios)
        return True, f"💖 '{entrada}' marcada como favorita."

    def ver_pelicula(self, id_pelicula):
        """Registra visualización de la película según su ID."""
        if not self.usuario_actual:
            return False, "⚠ Debes iniciar sesión primero."

        peli = next((p for p in self.catalogo.peliculas if p.id_pelicula == id_pelicula), None)

        if not peli:
            return False, "⚠ Película no encontrada."

        gestor = Funciones._get_gestor() # Obtiene la instancia de GestorSQL
        # Llama al método registrar_visualizacion de esa instancia de GestorSQL
        # Pasamos el correo del usuario, el ID de la película y el título de la película
        gestor.registrar_visualizacion(self.usuario_actual.correo, peli.id_pelicula, peli.titulo)

        return True, f"🎥 Estás viendo '{peli.titulo} ({peli.año})' ¡Disfruta tu película!"