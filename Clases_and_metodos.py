import os
import json
import hashlib
import pandas as pd 
import logging

# ------------------- Clase Funciones -------------------
class Funciones:
    # Rutas de archivos
    ruta_json_normal = os.path.join(os.path.expanduser("~"), "Downloads", "Documentos Plataforma", "Archivo_usuarios_normales.json")
    ruta_json_premium = os.path.join(os.path.expanduser("~"), "Downloads", "Documentos Plataforma", "Archivo_usuarios_premium.json")
    ruta_visualizaciones = os.path.join(os.path.expanduser("~"), "Downloads", "Documentos Plataforma", "visualizaciones.json")

    @staticmethod
    def cifrar_contraseña(contraseña):
        return hashlib.sha256(contraseña.encode()).hexdigest()

    @staticmethod
    def cargar_usuarios(tipo="normal"):
        if tipo == "premium":
            ruta = Funciones.ruta_json_premium
        else:
            ruta = Funciones.ruta_json_normal
        
        if os.path.exists(ruta):
            with open(ruta, "r", encoding="utf-8") as archivo:
                return json.load(archivo)
        return {}

    @staticmethod
    def guardar_usuarios(usuarios, tipo="normal"):
        ruta = Funciones.ruta_json_premium if tipo == "premium" else Funciones.ruta_json_normal
        with open(ruta, "w", encoding="utf-8") as archivo:
            json.dump(usuarios, archivo, indent=4)

    @staticmethod
    def registrar_visualizacion(correo, pelicula):
        if os.path.exists(Funciones.ruta_visualizaciones):
            with open(Funciones.ruta_visualizaciones, "r", encoding="utf-8") as archivo:
                registros = json.load(archivo)
        else:
            registros = {"por_usuario": {}, "general": {}}
        
        registros.setdefault("por_usuario", {}).setdefault(correo, {}).setdefault("visualizaciones", {})
        
        nombre_pelicula = pelicula if isinstance(pelicula, str) else pelicula.titulo.strip()
        fecha_pelicula = "Desconocido" if isinstance(pelicula, str) else str(pelicula.año).strip()
        clave_pelicula = f"{nombre_pelicula} ({fecha_pelicula})"
        
        # Se garantiza que exista la clave antes de incrementar
        registros["por_usuario"][correo]["visualizaciones"].setdefault(clave_pelicula, 0)
        registros["por_usuario"][correo]["visualizaciones"][clave_pelicula] += 1
        
        registros.setdefault("general", {}).setdefault(clave_pelicula, 0)
        registros["general"][clave_pelicula] += 1
        
        with open(Funciones.ruta_visualizaciones, "w", encoding="utf-8") as archivo:
            json.dump(registros, archivo, indent=4)

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

# ------------------- Clases -------------------
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
        self.contraseña = Funciones.cifrar_contraseña(contraseña)
        self.correo = correo
        self.mi_lista = []
        self.favoritas = []

    def iniciar_sesion(self, usuarios):
        """Verifica credenciales y devuelve el usuario autenticado."""
        usuario_info = usuarios.get(self.correo)
        if not usuario_info:
            return False, "El correo no se encuentra registrado."
        
        if usuario_info.get("contraseña") != self.contraseña:
            return False, "Contraseña incorrecta."

        self.nombre = usuario_info["nombre"]
        self.mi_lista = usuario_info.get("mi_lista", [])
        self.favoritas = usuario_info.get("favoritas", [])
        self.historial_sesiones = usuario_info.get("historial_sesiones", [])
        return True, "Inicio de sesión exitoso."

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
        self.usuarios = Funciones.cargar_usuarios(tipo=tipo_usuarios)
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
        self.usuarios.setdefault(self.usuario_actual.correo, {})["mi_lista"] = self.usuario_actual.mi_lista
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
        self.usuarios.setdefault(self.usuario_actual.correo, {})["favoritas"] = self.usuario_actual.favoritas
        Funciones.guardar_usuarios(self.usuarios, tipo=self.tipo_usuarios)
        return True, f"💖 '{entrada}' marcada como favorita."

    def ver_pelicula(self, id_pelicula):
        """Registra visualización de la película según su ID."""
        if not self.usuario_actual:
            return False, "⚠ Debes iniciar sesión primero."
        
        peli = next((p for p in self.catalogo.peliculas if p.id_pelicula == id_pelicula), None)
        
        if not peli:
            return False, "⚠ Película no encontrada."
        
        Funciones.registrar_visualizacion(self.usuario_actual.correo, peli)
        return True, f"🎥 Estás viendo '{peli.titulo} ({peli.año})' ¡Disfruta tu película!"
    
