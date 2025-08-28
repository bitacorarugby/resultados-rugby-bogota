import streamlit as st
import pandas as pd
import os

# --- Configuración de la página ---
st.set_page_config(page_title="Resultados Rugby", layout="wide")
st.title("🏉 Resultados de Rugby")

# --- Función para cargar CSV desde GitHub ---
def load_data():
    url = "https://raw.githubusercontent.com/bitacorarugby/resultados-rugby-bogota/refs/heads/main/resultados%20bogota.csv"  # <- pon aquí tu URL raw de GitHub
    try:
        df = pd.read_csv(url)
        df["PuntosLocal"] = df["PuntosLocal"].astype(int)
        df["PuntosVisitante"] = df["PuntosVisitante"].astype(int)
        df["Jornada_num"] = df["Jornada"].str.extract("(\d+)").astype(int)
        return df
    except Exception as e:
        st.error(f"Error al cargar el CSV: {e}")
        return None

df = load_data()
if df is None:
    st.stop()

# --- Sidebar: filtros ---
st.sidebar.header("⚙️ Filtros")
competiciones = st.sidebar.multiselect("Competición", options=df["Competicion"].unique())
temporadas = st.sidebar.multiselect("Temporada", options=df["Temporada"].unique())
jornadas = st.sidebar.multiselect("Jornada", options=df["Jornada"].unique())
equipos = st.sidebar.multiselect("Equipo", options=pd.concat([df["Local"], df["Visitante"]]).unique())

# --- Sidebar: selección por equipo ---
st.sidebar.header("🔍 Ver equipo")
equipo_seleccionado = st.sidebar.selectbox(
    "Selecciona un equipo",
    options=[""] + sorted(df["Local"].unique().tolist())
)

# --- Aplicar filtros ---
df_filtrado = df.copy()
if competiciones:
    df_filtrado = df_filtrado[df_filtrado["Competicion"].isin(competiciones)]
if temporadas:
    df_filtrado = df_filtrado[df_filtrado["Temporada"].isin(temporadas)]
if jornadas:
    df_filtrado = df_filtrado[df_filtrado["Jornada"].isin(jornadas)]
if equipos:
    df_filtrado = df_filtrado[(df_filtrado["Local"].isin(equipos)) | (df_filtrado["Visitante"].isin(equipos))]

# --- Próxima jornada ---
ultima_jornada_num = df_filtrado["Jornada_num"].max()
proxima_jornada_num = ultima_jornada_num + 1
proxima_jornada = df_filtrado[df_filtrado["Jornada_num"] == proxima_jornada_num]

# --- Función para mostrar partido ---
def mostrar_partido(row):
    col1, col2, col3 = st.columns([3,1,3])
    with col1:
        logo_local = f"logos/{row['Local']}.png"
        if os.path.exists(logo_local):
            st.image(logo_local, width=50)
        st.markdown(f"### {row['Local']}")
    with col2:
        st.markdown(f"## {row['PuntosLocal']} - {row['PuntosVisitante']}")
    with col3:
        logo_visitante = f"logos/{row['Visitante']}.png"
        if os.path.exists(logo_visitante):
            st.image(logo_visitante, width=50)
        st.markdown(f"### {row['Visitante']}")
    st.caption(f"{row['Competicion']} | {row['Temporada']} | Jornada {row['Jornada']}")
    st.markdown("---")

# --- Mostrar próxima jornada ---
st.subheader("📅 Próxima Fecha")
if not proxima_jornada.empty:
    for _, row in proxima_jornada.iterrows():
        mostrar_partido(row)
else:
    st.info("No hay partidos programados para la próxima jornada")

# --- Mostrar partidos ---
if not equipo_seleccionado:
    st.subheader("📋 Partidos")
    for _, row in df_filtrado.iterrows():
        mostrar_partido(row)
else:
    st.subheader(f"📌 Detalles de {equipo_seleccionado}")
    partidos_equipo = df_filtrado[
        (df_filtrado["Local"] == equipo_seleccionado) | (df_filtrado["Visitante"] == equipo_seleccionado)
    ]
    for _, row in partidos_equipo.iterrows():
        mostrar_partido(row)

# --- Tabla de posiciones con logos ---
st.subheader("🏆 Tabla de posiciones")

# Calcular clasificación
equipos_dict = {}
for _, row in df_filtrado.iterrows():
    local, visitante = row["Local"], row["Visitante"]
    pl, pv = row["PuntosLocal"], row["PuntosVisitante"]
    for eq in [local, visitante]:
        if eq not in equipos_dict:
            equipos_dict[eq] = {"PJ":0, "PG":0, "PE":0, "PP":0, "PF":0, "PC":0, "Puntos":0}
    equipos_dict[local]["PJ"] += 1
    equipos_dict[visitante]["PJ"] += 1
    equipos_dict[local]["PF"] += pl
    equipos_dict[local]["PC"] += pv
    equipos_dict[visitante]["PF"] += pv
    equipos_dict[visitante]["PC"] += pl
    if pl > pv:
        equipos_dict[local]["PG"] += 1
        equipos_dict[visitante]["PP"] += 1
        equipos_dict[local]["Puntos"] += 4
        equipos_dict[visitante]["Puntos"] += 0
        if (pl - pv) <= 7:
            equipos_dict[visitante]["Puntos"] += 1
    elif pv > pl:
        equipos_dict[visitante]["PG"] += 1
        equipos_dict[local]["PP"] += 1
        equipos_dict[visitante]["Puntos"] += 4
        equipos_dict[local]["Puntos"] += 0
        if (pv - pl) <= 7:
            equipos_dict[local]["Puntos"] += 1
    else:
        equipos_dict[local]["PE"] += 1
        equipos_dict[visitante]["PE"] += 1
        equipos_dict[local]["Puntos"] += 2
        equipos_dict[visitante]["Puntos"] += 2

clasificacion = pd.DataFrame.from_dict(equipos_dict, orient="index").reset_index()
clasificacion.rename(columns={"index":"Equipo"}, inplace=True)
clasificacion["Dif"] = clasificacion["PF"] - clasificacion["PC"]
clasificacion = clasificacion.sort_values(by=["Puntos","Dif"], ascending=[False, False])

# --- Generar tabla HTML con logos ---
html_table = "<table style='width:100%; border-collapse: collapse;'>"
html_table += "<tr style='background-color:#EEE;'><th>Logo</th><th>Equipo</th><th>PJ</th><th>PG</th><th>PE</th><th>PP</th><th>PF</th><th>PC</th><th>Dif</th><th>Puntos</th></tr>"

for _, row in clasificacion.iterrows():
    logo_path = f"logos/{row['Equipo']}.png"
    if os.path.exists(logo_path):
        logo_html = f"<img src='{logo_path}' width='30'>"
    else:
        logo_html = ""
    html_table += f"<tr style='text-align:center;'><td>{logo_html}</td><td>{row['Equipo']}</td><td>{row['PJ']}</td><td>{row['PG']}</td><td>{row['PE']}</td><td>{row['PP']}</td><td>{row['PF']}</td><td>{row['PC']}</td><td>{row['Dif']}</td><td>{row['Puntos']}</td></tr>"

html_table += "</table>"

st.markdown(html_table, unsafe_allow_html=True)
