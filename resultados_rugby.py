import streamlit as st
import pandas as pd

# ----------------------------
# URLs
# ----------------------------
LOGO_BASE_URL = "https://raw.githubusercontent.com/bitacorarugby/resultados-rugby-bogota/main/logos/"
CSV_URL = "https://raw.githubusercontent.com/bitacorarugby/resultados-rugby-bogota/main/resultados_bogota.csv"

# ----------------------------
# Cargar CSV
# ----------------------------
@st.cache_data
def load_data():
    return pd.read_csv(CSV_URL)

try:
    df = load_data()
except Exception as e:
    st.error(f"Error al cargar el CSV: {e}")
    st.stop()

st.title("🏉 Resultados - Ligas Nacionales")

# ----------------------------
# Filtros
# ----------------------------
st.sidebar.header("Filtros")
competicion = st.sidebar.multiselect("Competición", df["Competicion"].unique())
temporada = st.sidebar.multiselect("Temporada", df["Temporada"].unique())
jornada = st.sidebar.multiselect("Jornada", df["Jornada"].unique())

df_filtered = df.copy()
if competicion:
    df_filtered = df_filtered[df_filtered["Competicion"].isin(competicion)]
if temporada:
    df_filtered = df_filtered[df_filtered["Temporada"].isin(temporada)]
if jornada:
    df_filtered = df_filtered[df_filtered["Jornada"].isin(jornada)]

# ----------------------------
# Estilos CSS para hover
# ----------------------------
st.markdown("""
<style>
.match-row {
    display: flex; 
    align-items: center; 
    justify-content: center; 
    gap: 15px; 
    font-size: 16px; 
    margin-bottom:5px; 
    padding:5px;
    border-radius:5px;
    transition: background-color 0.2s ease;
}
.match-row:hover {
    background-color: #f0f8ff;
}
.match-info {
    font-size: 14px; 
    color: #555;
}
</style>
""", unsafe_allow_html=True)

# ----------------------------
# Mostrar resultados con hover
# ----------------------------
for _, row in df_filtered.iterrows():
    logo_local = f"{LOGO_BASE_URL}{row['Local']}.png"
    logo_visitante = f"{LOGO_BASE_URL}{row['Visitante']}.png"

    local_html = f"<img src='{logo_local}' width='25' style='vertical-align:middle'> <b>{row['Local']}</b>" if logo_local else f"<b>{row['Local']}</b>"
    visitante_html = f"<b>{row['Visitante']}</b> <img src='{logo_visitante}' width='25' style='vertical-align:middle'>" if logo_visitante else f"<b>{row['Visitante']}</b>"
    marcador_html = f"<span style='background-color:#f0f0f0; padding:5px 10px; border-radius:5px;'>{row['PuntosLocal']} - {row['PuntosVisitante']}</span>"

    # Competición, temporada y jornada
    info_html = f"<span class='match-info'>{row['Competicion']} | {row['Temporada']} | {row['Jornada']}</span>"

    st.markdown(
        f"""
        <div class='match-row'>
            {local_html} {marcador_html} {visitante_html} {info_html}
        </div>
        """,
        unsafe_allow_html=True
    )
    st.markdown("<hr style='border:0.5px solid #ddd'>", unsafe_allow_html=True)

# ----------------------------
# Tabla de posiciones
# ----------------------------
st.header("📊 Tabla de posiciones")
tabla = (
    df.groupby("Local")
    .agg({"PuntosLocal": "sum"})
    .rename(columns={"PuntosLocal": "Puntos"})
    .reset_index()
    .sort_values(by="Puntos", ascending=False)
)
st.dataframe(tabla, hide_index=True)
