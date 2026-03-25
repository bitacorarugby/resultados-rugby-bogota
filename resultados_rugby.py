import streamlit as st
import pandas as pd

# ----------------------------
# CONFIG
# ----------------------------
st.set_page_config(page_title="Resultados Rugby", layout="wide")

EXCEL_URL = "https://raw.githubusercontent.com/bitacorarugby/resultados-rugby-bogota/main/resultados_bogota.xlsx"
LOGO_BASE_URL = "https://raw.githubusercontent.com/bitacorarugby/resultados-rugby-bogota/main/logos/"

# ----------------------------
# LOAD DATA
# ----------------------------
@st.cache_data
def load_data():
    df = pd.read_excel(EXCEL_URL)

    # Renombrar columnas para simplificar el código
    df = df.rename(columns={
        "Equipo Local": "Local",
        "Equipo Visitante": "Visitante",
        "Puntaje Local": "PuntosLocal",
        "Puntaje Visitante": "PuntosVisitante",
        "Liga": "Competicion",
        "Categoria": "Temporada"
    })

    return df

df = load_data()

# ----------------------------
# SIDEBAR
# ----------------------------
st.sidebar.header("Filtros")

comp = st.sidebar.multiselect("Liga", df["Competicion"].unique())
temp = st.sidebar.multiselect("Categoría", df["Temporada"].unique())
jor = st.sidebar.multiselect("Jornada", df["Jornada"].unique())

df_filtered = df.copy()

if comp:
    df_filtered = df_filtered[df_filtered["Competicion"].isin(comp)]
if temp:
    df_filtered = df_filtered[df_filtered["Temporada"].isin(temp)]
if jor:
    df_filtered = df_filtered[df_filtered["Jornada"].isin(jor)]

# ----------------------------
# TITLE
# ----------------------------
st.title("🏉 Resultados Rugby Bogotá")

# ----------------------------
# CSS CARDS
# ----------------------------
st.markdown("""
<style>
.match-card {
    background-color: white;
    padding: 12px;
    border-radius: 10px;
    margin-bottom: 10px;
    box-shadow: 0 2px 6px rgba(0,0,0,0.08);
    transition: transform 0.15s ease, box-shadow 0.15s ease;
}

.match-card:hover {
    transform: scale(1.01);
    box-shadow: 0 4px 10px rgba(0,0,0,0.12);
}

.match-row {
    display: flex;
    align-items: center;
    justify-content: space-between;
}

.team {
    display: flex;
    align-items: center;
    gap: 6px;
    font-weight: 600;
}

.score {
    background-color: #f0f0f0;
    padding: 6px 12px;
    border-radius: 6px;
    font-weight: bold;
    font-size: 16px;
}

.match-info {
    text-align: center;
    font-size: 13px;
    color: #666;
    margin-top: 4px;
}
</style>
""", unsafe_allow_html=True)

# ----------------------------
# MATCH CARDS
# ----------------------------
for _, row in df_filtered.iterrows():

    logo_local = f"{LOGO_BASE_URL}{row['Local']}.png"
    logo_visitante = f"{LOGO_BASE_URL}{row['Visitante']}.png"

    st.markdown(f"""
    <div class="match-card">
        <div class="match-row">

            <div class="team">
                <img src="{logo_local}" width="28">
                {row['Local']}
            </div>

            <div class="score">
                {row['PuntosLocal']} - {row['PuntosVisitante']}
            </div>

            <div class="team">
                {row['Visitante']}
                <img src="{logo_visitante}" width="28">
            </div>

        </div>

        <div class="match-info">
            {row['Competicion']} | {row['Temporada']} | {row['Jornada']}
        </div>
    </div>
    """, unsafe_allow_html=True)

# ----------------------------
# TABLA POSICIONES
# ----------------------------
st.header("🏆 Tabla de posiciones")

equipos = {}

for _, row in df.iterrows():
    local, visitante = row["Local"], row["Visitante"]
    pl, pv = row["PuntosLocal"], row["PuntosVisitante"]

    for eq in [local, visitante]:
        if eq not in equipos:
            equipos[eq] = {"PJ":0, "PG":0, "PP":0, "PF":0, "PC":0, "PTS":0}

    equipos[local]["PJ"] += 1
    equipos[visitante]["PJ"] += 1

    equipos[local]["PF"] += pl
    equipos[local]["PC"] += pv

    equipos[visitante]["PF"] += pv
    equipos[visitante]["PC"] += pl

    if pl > pv:
        equipos[local]["PG"] += 1
        equipos[visitante]["PP"] += 1
        equipos[local]["PTS"] += 4
    elif pv > pl:
        equipos[visitante]["PG"] += 1
        equipos[local]["PP"] += 1
        equipos[visitante]["PTS"] += 4
    else:
        equipos[local]["PTS"] += 2
        equipos[visitante]["PTS"] += 2

tabla = pd.DataFrame.from_dict(equipos, orient="index").reset_index()
tabla.rename(columns={"index":"Equipo"}, inplace=True)
tabla["Dif"] = tabla["PF"] - tabla["PC"]

tabla = tabla.sort_values(by=["PTS","Dif"], ascending=False)

st.dataframe(tabla, use_container_width=True)
