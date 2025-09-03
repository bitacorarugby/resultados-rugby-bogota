import streamlit as st
import pandas as pd

# ----------------------------
# Configuración de URLs
# ----------------------------

# URL base de la carpeta de logos en tu repo (usar raw)
LOGO_BASE_URL = "https://raw.githubusercontent.com/bitacorarugby/resultados-rugby-bogota/main/logos/"

# CSV en GitHub (raw)
CSV_URL = "https://raw.githubusercontent.com/bitacorarugby/resultados-rugby-bogota/main/resultados_bogota.csv"

# ----------------------------
# Función para cargar CSV
# ----------------------------
@st.cache_data
def load_data():
    return pd.read_csv(CSV_URL)

try:
    df = load_data()
except Exception as e:
    st.error(f"Error al cargar el CSV: {e}")
    st.stop()

# ----------------------------
# Título
# ----------------------------
st.title("🏉 Resultados de Rugby")

# ----------------------------
# Sidebar con filtros
# ----------------------------
st.sidebar.header("Filtros")
competicion = st.sidebar.multiselect("Competición", df["Competicion"].unique())
temporada = st.sidebar.multiselect("Temporada", df["Temporada"].unique())
jornada = st.sidebar.multiselect("Jornada", df["Jornada"].unique())

# Aplicar filtros
df_filtered = df.copy()
if competicion:
    df_filtered = df_filtered[df_filtered["Competicion"].isin(competicion)]
if temporada:
    df_filtered = df_filtered[df_filtered["Temporada"].isin(temporada)]
if jornada:
    df_filtered = df_filtered[df_filtered["Jornada"].isin(jornada)]

# ----------------------------
# Mostrar resultados con logos
# ----------------------------
for _, row in df_filtered.iterrows():
    col1, col2, col3, col4, col5 = st.columns([1, 3, 1, 3, 1])

    # Construir URL del logo local y visitante
    logo_local = f"{LOGO_BASE_URL}{row['Local']}.png"
    logo_visitante = f"{LOGO_BASE_URL}{row['Visitante']}.png"

    # Logo local
    try:
        col1.image(logo_local, width=40)
    except:
        pass  # Si no existe, deja vacío

    # Nombre local
    col2.markdown(f"**{row['Local']}**")

    # Marcador
    col3.markdown(f"### {row['PuntosLocal']} - {row['PuntosVisitante']}")

    # Nombre visitante
    col4.markdown(f"**{row['Visitante']}**")

    # Logo visitante
    try:
        col5.image(logo_visitante, width=40)
    except:
        pass

    st.divider()

# ----------------------------
# Tabla de posiciones
# ----------------------------
st.header("📊 Tabla de posiciones")

# Calculamos los puntos por equipo
tabla = (
    df.groupby("Local")
    .agg({"PuntosLocal": "sum"})
    .rename(columns={"PuntosLocal": "Puntos"})
    .reset_index()
)

st.dataframe(tabla, hide_index=True)
