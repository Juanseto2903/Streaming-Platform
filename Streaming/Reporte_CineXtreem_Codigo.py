import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.application import MIMEApplication
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from fpdf import FPDF
import os

EMAIL_QUIEN_ENVIA = ""

PARA = [""]  # puedes agregar más correos aquí

MI_CONTRA = ""  # contraseña de aplicación

# Configuración general
sns.set(style="darkgrid")
plt.rcParams.update({'figure.autolayout': True})

# Archivos
ruta_base = os.path.join(os.path.dirname(__file__), 'Streaming', 'Recursos')
logo_path = os.path.join(ruta_base, "Logaso.png")
csv_path = os.path.join(ruta_base,"imdb_movies.csv")
output_pdf = os.path.join(os.path.expanduser("~"), "Downloads", "Reporte_CineXtreem_Final.pdf")

# Cargar datos
if not os.path.exists(csv_path):
    raise FileNotFoundError(f"❌ El archivo no se encuentra: {os.path.abspath(csv_path)}")

df = pd.read_csv(csv_path)
df.rename(columns={"names": "titulo", "date_x": "fecha", "score": "puntaje", "genre": "genero"}, inplace=True)
df["puntaje"] = pd.to_numeric(df["puntaje"], errors="coerce") / 10
df["genero"] = df["genero"].astype(str)
df["genero_principal"] = df["genero"].apply(lambda x: x.split(",")[0].strip())
df["fecha"] = pd.to_datetime(df["fecha"], errors='coerce')
df.dropna(subset=["titulo", "puntaje", "genero_principal", "fecha"], inplace=True)

# Función para gráficas
def crear_grafica(path, plot_func):
    plt.figure(figsize=(10, 6))
    plot_func()
    plt.savefig(path)
    plt.close()

# Gráficas
graf1 = "graf1_top_peliculas.png"
crear_grafica(graf1, lambda: df.groupby("titulo")["puntaje"].mean().sort_values(ascending=False).head(10).plot(kind="barh", color="skyblue", title="Top 10 Películas Mejor Calificadas"))

graf2 = "graf2_generos.png"
crear_grafica(graf2, lambda: sns.barplot(
    x=df["genero_principal"].value_counts().head(10).values,
    y=df["genero_principal"].value_counts().head(10).index,
    palette="muted"
).set_title("Distribución de Películas por Género"))

graf3 = "graf3_puntaje_genero.png"
crear_grafica(graf3, lambda: df.groupby("genero_principal")["puntaje"].mean().sort_values(ascending=False).head(10).plot(kind="barh", color="salmon", title="Promedio de Puntaje por Género"))

graf4 = "graf4_pastel_genero.png"
crear_grafica(graf4, lambda: df["genero_principal"].value_counts().head(5).plot.pie(autopct='%1.1f%%', ylabel="", title="Distribución Porcentual por Género"))

graf5 = "graf5_lineal_puntaje_tiempo.png"
crear_grafica(graf5, lambda: df.sort_values("fecha").groupby(df["fecha"].dt.to_period("Y"))["puntaje"].mean().plot(title="Evolución del Puntaje Promedio en el Tiempo", xlabel="Año", ylabel="Puntaje Promedio"))

graf6 = "graf6_dispersion_puntaje_fecha.png"
plt.figure(figsize=(10, 6))
sns.scatterplot(data=df, x="fecha", y="puntaje", hue="genero_principal")
plt.title("Relación entre Fecha de Estreno y Puntaje")
plt.xlabel("Fecha")
plt.ylabel("Puntaje")
plt.legend(loc="upper left")
plt.savefig(graf6)
plt.close()

# Crear PDF
pdf = FPDF()
pdf.set_auto_page_break(auto=True, margin=15)

# Portada tipo informe anual
pdf.add_page()
if os.path.exists(logo_path):
    pdf.image(logo_path, x=10, y=10, w=35)


pdf.set_text_color(0, 0, 0)
pdf.set_font("Arial", "B", 16)
pdf.ln(50)  # Espacio después del logo
pdf.cell(0, 10, "Informe Estadístico de CineXtreem", ln=True, align="C")

pdf.ln(15)
pdf.set_font("Arial", "B", 12)
pdf.cell(0, 10, "Ingenieria De Datos e IA", ln=True, align="C")

pdf.ln(20)
pdf.set_font("Arial", "", 12)
pdf.cell(0, 10, "Elaborado por:", ln=True, align="C")

pdf.ln(5)
pdf.set_font("Arial", "B", 12)
pdf.cell(0, 10, "Juan Sebastian Torres", ln=True, align="C")
pdf.cell(0, 10, "Juan Felipe Aristizabal", ln=True, align="C")
pdf.cell(0, 10, "Sebastian Manrique Mejia", ln=True, align="C")

pdf.ln(20)
pdf.set_font("Arial", "B", 12)
pdf.cell(0, 10, "Universidad Autonoma De Occidente", ln=True, align="C")
pdf.cell(0, 10, "Santiago De Cali", ln=True, align="C")

pdf.ln(15)
pdf.set_font("Arial", "", 12)
pdf.cell(0, 10, "27/05/2025", ln=True, align="C")



# Página de introducción
pdf.add_page()
if os.path.exists(logo_path):
    pdf.image(logo_path, x=60, y=10, w=90)
pdf.ln(60)
pdf.set_font("Arial", "B", 16)
pdf.cell(0, 10, "Datos de CineXtreem", ln=True, align="C")
pdf.ln(10)
pdf.set_font("Arial", size=12)
intro = (
    "CineXtreem, como plataforma líder de análisis y recomendación de películas, presenta el siguiente "
    "informe con el objetivo de ofrecer una visión clara sobre el comportamiento de las calificaciones y géneros "
    "en una base de datos representativa de producciones cinematográficas. Este documento recopila estadísticas clave "
    "y visualizaciones gráficas que permiten comprender la calidad media de las películas, sus géneros más comunes y "
    "la evolución temporal del puntaje.\n\n"
    "El análisis se ha elaborado utilizando herramientas de ciencia de datos, generando representaciones visuales "
    "que incluyen gráficos de barras, pastel, líneas y dispersión. Los resultados son de utilidad tanto para empresas "
    "de streaming como para cinéfilos que buscan comprender mejor el mercado del cine."
)
pdf.multi_cell(0, 10, intro)

# Descripción de datos
pdf.set_font("Arial", "B", 14)
pdf.cell(0, 10, "Resumen de Variables ", ln=True)
pdf.set_font("Arial", size=12)
descripcion = (
    "- Título: nombre oficial de la película.\n"
    "- Fecha: día de estreno.\n"
    "- Puntaje: calificación promedio de usuarios (0 a 10).\n"
    "- Género: categoría principal (ej. Acción, Comedia, etc.).\n\n"
    "El puntaje fue convertido de una escala 0-100 a 0-10. En caso de múltiples géneros, "
    "se utilizó el primero como principal para simplificar el análisis."
)
pdf.multi_cell(0, 10, descripcion)

# Insertar gráficas
def agregar_grafica(titulo, ruta):
    pdf.add_page()
    pdf.set_font("Arial", "B", 14)
    pdf.cell(0, 10, titulo, ln=True)
    pdf.image(ruta, x=15, w=180)

graficas = [
    ("Top 10 Películas Mejor Calificadas", graf1),
    ("Distribución de Películas por Género", graf2),
    ("Promedio de Puntaje por Género", graf3),
    ("Distribución Porcentual por Género", graf4),
    ("Evolución del Puntaje Promedio en el Tiempo", graf5),
    ("Relación entre Fecha de Estreno y Puntaje", graf6),
]
for titulo, ruta in graficas:
    agregar_grafica(titulo, ruta)

# Conclusión
pdf.add_page()
pdf.set_font("Arial", "B", 14)
pdf.cell(0, 10, "Conclusiones", ln=True)
pdf.set_font("Arial", size=12)
conclusion = (
    "Gracias a este análisis estadístico se puede destacar lo siguiente:\n\n"
    "- Los géneros más representados en la base de datos tienden a ser Acción, Drama y Comedia.\n"
    "- El puntaje promedio ha variado a lo largo del tiempo, con una ligera mejora en los últimos años.\n"
    "- La correlación entre la fecha de estreno y el puntaje revela tendencias en la evolución del gusto del público.\n"
    "- Los gráficos permiten identificar de forma visual cuáles géneros mantienen mejores promedios de calificación.\n\n"
    "Este informe sirve como base para decisiones editoriales, recomendaciones personalizadas y desarrollo de contenido "
    "en plataformas de distribución de películas como CineXtreem."
)
pdf.multi_cell(0, 10, conclusion)

# Guardar PDF
pdf.output(output_pdf)
print(f"✅ PDF generado en: {output_pdf}")

# ENVIAR EMAIL (IMPORTANTE REVISAR QUE ESTE COMENTADO SI NO SE VA A ENVIAR)

def send_email():
    """Envía el PDF generado por Gmail"""
    msg = MIMEMultipart()
    msg['From'] = EMAIL_QUIEN_ENVIA
    msg['Bcc'] = ", ".join(PARA)
    msg['Subject'] = "Informe Estadístico de CineXtreem"

    body = """
    Buenas noches compañeros y profesor,

    A continuación se encuentra adjunto el informe estadístico generado por el siguiente grupo de trabajo:
    - Juan Sebastian Torres
    - Juan Felipe Aristizabal
    - Sebastian Manrique Mejia
    
    Incluye gráficas y análisis detallado de películas.

    Docente: Andrés Felipe Rodríguez.

    Saludos,
    Equipo CineXtreem \U0001F3A5
    """
    msg.attach(MIMEText(body, 'plain'))

    with open(output_pdf, "rb") as f:
        attach = MIMEApplication(f.read(), _subtype="pdf")
        attach.add_header('Content-Disposition', 'attachment', filename=os.path.basename(output_pdf))
        msg.attach(attach)

    try:
        with smtplib.SMTP('smtp.gmail.com', 587) as server:
            server.starttls()
            server.login(EMAIL_QUIEN_ENVIA, MI_CONTRA)
            server.send_message(msg)
        print("✅ Correo enviado con éxito.")
    except Exception as e:
        print(f"❌ Error al enviar el correo: {str(e)}")

# send_email()

