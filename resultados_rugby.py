import streamlit as st
import pandas as pd

# ------------------------
# CONFIG
# ------------------------
st.set_page_config(page_title="Resultados Rugby Bogotá", layout="wide")

CSV_URL = "https://raw.githubusercontent.com/bitacorarugby/resultados-rugby-bogota/refs/heads/main/resultados_bogota.csv"

# Diccionario de logos
LOGOS = {
    "Carneros": "https://upload.wikimedia.org/wikipedia/commons/3/3f/Placeholder_view_vector.svg",
    "Barbarians": "https://upload.wikimedia.org/wikipedia/commons/3/3f/Placeholder_view_vector.svg",
    "Espartanos": "https://upload.wikimedia.org/wikipedia/commons/3/3f/Placeholder_view_vector.svg",
    "Petirrojos": "https://upload.wikimedia.org/wikipedia/commons/3/3f/Placeholder_view_vector.svg",
    "Duendes": "https://upload.wikimedia.org/wikipedia/commons/3/3f/Placeholder_view_vector.svg",
    "Gatos": "https://upload.wikimedia.org/wikipedia/commons/3/3f/Placeholder_view_vector.svg",
    "Manoba": "https://upload.wikimedia.org/wikipedia/commons/3/3f/Placeholder_view_vector.svg",
    "Cachacas": "https://upload.wikimedia.org/wikipedia/commons/3/3f/Placeholder_view_vector.svg",
    "Jaguares": "https://upload.wikimedia.org/wikipedia/commons/3/3f/Placeholder_view_vector.svg",
    "Coyotes": "https://upload.wikimedia.org/wikipedia/commons/3/3f/Placeholder_view_vector.svg",
    "Alianza": "https://upload.wikimedia.org/wikipedia/commons/3/3f/Placeholder_view_vector.svg",
    "Minotauros": "https://upload.wikimedia.org/wikipedia/commons/3/3f/Placeholder_view_vector.svg",
    "Zeppelin": "https://upload.wikimedia.org/wikipedia/commons/3/3f/Placeholder_view_vector.svg"
}

# ------------------------
# Cargar CSV
# ------------------------
@st.cache_data
def load_data():
    try:
        df = pd.read_csv(CSV_URL)
        return df
    except Exception as e:
        st.error(f"Error al cargar el CSV: {e}")
        return pd.DataFrame()

df = load_data()

if df.empty:
    st.stop()

# ------------------------
# Barra lateral - filtros
# ------------------------
st.sidebar.header("Filtros")
comp = st.sidebar.multiselect("Competición", options=df["Competicion"].unique(), default=df["Competicion"].unique())
temp = st.sidebar.multiselect("Temporada", options=df["Temporada"].unique(), default=df["Temporada"].unique())
jor = st.sidebar.multiselect("Jornada", options=df["Jornada"].unique(), default=df["Jornada"].unique())

df_filtered = df[
    (df["Competicion"].isin(comp)) &
    (df["Temporada"].isin(temp)) &
    (df["Jornada"].isin(jor))
]

# ------------------------
# Mostrar resultados
# ------------------------
st.header("📊 Resultados")

for _, row in df_filtered.iterrows():
    col1, col2, col3 = st.columns([1, 2, 1])

    with col1:
        st.image(LOGOS.get(row["Local"], ""), width=50)
    with col2:
        # Formato compacto en 1 sola línea
        st.markdown(
            f"<div style='text-align:center; font-size:18px;'>"
            f"**{row['Local']} {row['PuntosLocal']} - {row['PuntosVisitante']} {row['Visitante']}**"
            f"</div>",
            unsafe_allow_html=True
        )
    with col3:
        st.image(LOGOS.get(row["Visitante"], ""), width=50)

st.markdown("---")

# ------------------------
# Tabla de posiciones
# ------------------------
st.header("🏆 Tabla de Posiciones")

def calcular_posiciones(data):
    equipos = {}
    for _, row in data.iterrows():
        local, visitante = row["Local"], row["Visitante"]
        pl, pv = row["PuntosLocal"], row["PuntosVisitante"]

        for eq in [local, visitante]:
            if eq not in equipos:
                equipos[eq] = {"PJ": 0, "PG": 0, "PP": 0, "PE": 0, "PF": 0, "PC": 0, "Pts": 0}

        equipos[local]["PJ"] += 1
        equipos[visitante]["PJ"] += 1
        equipos[local]["PF"] += pl
        equipos[local]["PC"] += pv
        equipos[visitante]["PF"] += pv
        equipos[visitante]["PC"] += pl

        if pl > pv:
            equipos[local]["PG"] += 1
            equipos[visitante]["PP"] += 1
            equipos[local]["Pts"] += 4
        elif pl < pv:
            equipos[visitante]["PG"] += 1
            equipos[local]["PP"] += 1
            equipos[visitante]["Pts"] += 4
        else:
            equipos[local]["PE"] += 1
            equipos[visitante]["PE"] += 1
            equipos[local]["Pts"] += 2
            equipos[visitante]["Pts"] += 2

    tabla = pd.DataFrame.from_dict(equipos, orient="index").reset_index()
    tabla = tabla.rename(columns={"index": "Equipo"})
    tabla = tabla.sort_values(by=["Pts", "PG", "PF"], ascending=[False, False, False]).reset_index(drop=True)
    return tabla

tabla = calcular_posiciones(df)
st.dataframe(tabla, hide_index=True, use_container_width=True)
