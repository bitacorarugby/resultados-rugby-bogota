import streamlit as st
import pandas as pd

st.set_page_config(page_title="Resultados Rugby", layout="wide")

st.title("🏉 Resultados de Rugby")

# --- Cargar CSV desde GitHub (raw) ---
CSV_URL = "https://raw.githubusercontent.com/bitacorarugby/resultados-rugby-bogota/main/resultados_bogota.csv"

try:
    df = pd.read_csv(CSV_URL)
    df.columns = df.columns.str.strip()  # limpiar espacios en encabezados
except Exception as e:
    st.error(f"Error al cargar el CSV: {e}")
    st.stop()

# ----- SIDEBAR -----
st.sidebar.header("⚙️ Filtros")

competiciones = st.sidebar.multiselect("Competición", options=df["Competicion"].unique())
temporadas = st.sidebar.multiselect("Temporada", options=df["Temporada"].unique())
jornadas = st.sidebar.multiselect("Jornada", options=df["Jornada"].unique())
equipos = st.sidebar.multiselect("Equipo", options=pd.concat([df["Local"], df["Visitante"]]).unique())

# Aplicar filtros
if competiciones:
    df = df[df["Competicion"].isin(competiciones)]
if temporadas:
    df = df[df["Temporada"].isin(temporadas)]
if jornadas:
    df = df[df["Jornada"].isin(jornadas)]
if equipos:
    df = df[(df["Local"].isin(equipos)) | (df["Visitante"].isin(equipos))]

# ----- Configuración del sistema de puntos -----
st.sidebar.header("🏆 Sistema de puntos")
pts_victoria = st.sidebar.number_input("Puntos por victoria", min_value=0, value=4)
pts_empate = st.sidebar.number_input("Puntos por empate", min_value=0, value=2)
pts_derrota = st.sidebar.number_input("Puntos por derrota", min_value=0, value=0)
bonus_ofensivo = st.sidebar.number_input("Bonus ofensivo (ej: marcar 4 tries)", min_value=0, value=1)
bonus_defensivo = st.sidebar.number_input("Bonus defensivo (perder por -7)", min_value=0, value=1)

# ----- Mostrar Partidos -----
st.subheader("📋 Partidos filtrados")

for _, row in df.iterrows():
    st.markdown(
        f"""
        <div style="display:flex; align-items:center; justify-content:center; font-size:18px; margin:6px 0;">
            <img src="https://raw.githubusercontent.com/bitacorarugby/resultados-rugby-bogota/main/logos/{row['Local']}.png" width="26" style="margin-right:6px;">
            <b>{row['Local']}</b> {row['PuntosLocal']} - {row['PuntosVisitante']} <b>{row['Visitante']}</b>
            <img src="https://raw.githubusercontent.com/bitacorarugby/resultados-rugby-bogota/main/logos/{row['Visitante']}.png" width="26" style="margin-left:6px;">
        </div>
        <div style="text-align:center; font-size:13px; color:gray;">
            {row['Competicion']} | {row['Temporada']} | {row['Jornada']}
        </div>
        <hr style="border:0.5px solid #ddd; margin:6px 0;">
        """,
        unsafe_allow_html=True
    )

# ----- Clasificación -----
st.subheader("🏆 Clasificación")

equipos_dict = {}
for _, row in df.iterrows():
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

    if pl > pv:  # Gana local
        equipos_dict[local]["PG"] += 1
        equipos_dict[visitante]["PP"] += 1
        equipos_dict[local]["Puntos"] += pts_victoria
        equipos_dict[visitante]["Puntos"] += pts_derrota
        if (pl - pv) <= 7:
            equipos_dict[visitante]["Puntos"] += bonus_defensivo
    elif pv > pl:  # Gana visitante
        equipos_dict[visitante]["PG"] += 1
        equipos_dict[local]["PP"] += 1
        equipos_dict[visitante]["Puntos"] += pts_victoria
        equipos_dict[local]["Puntos"] += pts_derrota
        if (pv - pl) <= 7:
            equipos_dict[local]["Puntos"] += bonus_defensivo
    else:  # Empate
        equipos_dict[local]["PE"] += 1
        equipos_dict[visitante]["PE"] += 1
        equipos_dict[local]["Puntos"] += pts_empate
        equipos_dict[visitante]["Puntos"] += pts_empate

clasificacion = pd.DataFrame.from_dict(equipos_dict, orient="index").reset_index()
clasificacion.rename(columns={"index":"Equipo"}, inplace=True)
clasificacion["Dif"] = clasificacion["PF"] - clasificacion["PC"]
clasificacion = clasificacion.sort_values(by=["Puntos","Dif"], ascending=[False, False])

# Agregar logo en la tabla
def logo_path(equipo):
    return f"https://raw.githubusercontent.com/bitacorarugby/resultados-rugby-bogota/main/logos/{equipo}.png"

clasificacion["Logo"] = clasificacion["Equipo"].apply(lambda x: f'<img src="{logo_path(x)}" width="26">')

st.write(
    clasificacion.to_html(escape=False, index=False),
    unsafe_allow_html=True
)
