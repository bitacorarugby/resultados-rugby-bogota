import streamlit as st
import pandas as pd

# --- Configuración de la página ---
st.set_page_config(
    page_title="Resultados Rugby",
    page_icon="🏉",
    layout="wide"
)

st.title("🏉 Resultados de Rugby")

# --- Cargar CSV desde el repositorio ---
@st.cache_data
def load_data():
    try:
        df = pd.read_csv("resultados bogota.csv")
        return df
    except Exception as e:
        st.error(f"Error al cargar el CSV: {e}")
        return None
df = load_data()

if df is not None:
    # --- Barra lateral con filtros ---
    st.sidebar.header("Filtros")

    competiciones = st.sidebar.multiselect("Competición", options=df["Competicion"].unique())
    temporadas = st.sidebar.multiselect("Temporada", options=df["Temporada"].unique())
    jornadas = st.sidebar.multiselect("Jornada", options=df["Jornada"].unique())
    equipos = st.sidebar.multiselect(
        "Equipo", 
        options=pd.concat([df["Local"], df["Visitante"]]).unique()
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
        df_filtrado = df_filtrado[
            df_filtrado["Local"].isin(equipos) | df_filtrado["Visitante"].isin(equipos)
        ]

    # --- Mostrar resultados ---
    st.subheader("📊 Resultados")
    st.dataframe(
        df_filtrado.style.set_table_styles(
            [{
                "selector": "thead th",
                "props": [("background-color", "#003366"), ("color", "white")]
            }]
        )
    )
