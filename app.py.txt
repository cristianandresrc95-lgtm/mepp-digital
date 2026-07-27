"""
==================================================================================
 APP: INCAVOLT - Mantenimiento Eléctrico Preventivo y Control de Inventario
 Ingenio Incauca
 Alcance: Cosechadoras John Deere/Case y Tractores Game
 Desarrollado por: Cristian Rubio · Encargado de Electricidad
==================================================================================
"""

import os
from datetime import datetime, date
import pandas as pd
import plotly.express as px
import streamlit as st
import streamlit.components.v1 as components

# ----------------------------------------------------------------------------
# MARCA DE LA APLICACIÓN
# ----------------------------------------------------------------------------
NOMBRE_APP = "IncaVolt"
SUBTITULO_APP = "Gestión de Mantenimiento e Inventario de Taller · Incauca"
DESARROLLADOR = "Cristian Rubio · Encargado de Electricidad de Cosechadoras"

st.set_page_config(
    page_title=f"{NOMBRE_APP} | Taller Eléctrico",
    page_icon="⚡",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ----------------------------------------------------------------------------
# ARCHIVOS LOCALES (Persistencia CSV para zonas sin señal)
# ----------------------------------------------------------------------------
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
ARCHIVO_INSPECCIONES = os.path.join(BASE_DIR, "inspecciones.csv")
ARCHIVO_INVENTARIO = os.path.join(BASE_DIR, "inventario_taller.csv")

COLUMNAS_INSPECCION = [
    "id", "fecha", "hora", "tipo_maquina", "identificador", "categoria",
    "componente", "estado", "material_usado", "cantidad_usada", "observaciones", "tecnico",
]

COLUMNAS_INVENTARIO = [
    "repuesto_id", "nombre_material", "categoria", "cantidad_disponible", "ubicacion_estante", "alerta_minimo"
]

CATEGORIAS = ["Sensor", "Relé", "Fusible", "Cableado / Ramal", "Luces / Señalización", "Bobina", "Electrovalvula", "Otro"]
TIPOS_MAQUINA = ["Cosechadora John Deere", "Cosechadora Case", "Tractor Game"]
ESTADOS = ["Verde", "Amarillo", "Rojo"]

# ----------------------------------------------------------------------------
# CAPA DE DATOS
# ----------------------------------------------------------------------------
def _crear_archivo_si_no_existe(ruta, columnas):
    if not os.path.exists(ruta):
        pd.DataFrame(columns=columnas).to_csv(ruta, index=False)

def cargar_inspecciones() -> pd.DataFrame:
    _crear_archivo_si_no_existe(ARCHIVO_INSPECCIONES, COLUMNAS_INSPECCION)
    return pd.read_csv(ARCHIVO_INSPECCIONES, dtype=str).fillna("")

def guardar_inspecciones(df: pd.DataFrame):
    df.to_csv(ARCHIVO_INSPECCIONES, index=False)

def cargar_inventario() -> pd.DataFrame:
    _crear_archivo_si_no_existe(ARCHIVO_INVENTARIO, COLUMNAS_INVENTARIO)
    df = pd.read_csv(ARCHIVO_INVENTARIO, dtype=str).fillna("")
    if df.empty:
        # Inventario inicial de prueba para el taller si el archivo está en blanco
        datos_iniciales = [
            {"repuesto_id": "1", "nombre_material": "Sensor RPM John Deere", "categoria": "Sensor", "cantidad_disponible": "10", "ubicacion_estante": "A-1", "alerta_minimo": "2"},
            {"repuesto_id": "2", "nombre_material": "Relé 5 Pines 12V Heavy Duty", "categoria": "Relé", "cantidad_disponible": "25", "ubicacion_estante": "B-3", "alerta_minimo": "5"},
            {"repuesto_id": "3", "nombre_material": "Fusible 15A Tipo Ficha", "categoria": "Fusible", "cantidad_disponible": "50", "ubicacion_estante": "C-1", "alerta_minimo": "10"},
            {"repuesto_id": "4", "nombre_material": "Electrovalvula de Alce Tractor Game", "categoria": "Electrovalvula", "cantidad_disponible": "4", "ubicacion_estante": "D-2", "alerta_minimo": "1"},
        ]
        df = pd.DataFrame(datos_iniciales)
        df.to_csv(ARCHIVO_INVENTARIO, index=False)
    return df

def guardar_inventario(df: pd.DataFrame):
    df.to_csv(ARCHIVO_INVENTARIO, index=False)

def siguiente_id(df: pd.DataFrame, llave="id") -> int:
    if df.empty:
        return 1
    return int(pd.to_numeric(df[llave], errors="coerce").fillna(0).max()) + 1

# ----------------------------------------------------------------------------
# ESTILOS INTERFAZ
# ----------------------------------------------------------------------------
st.markdown(
    """
    <style>
    @import url('https://googleapis.com');
    html, body, [class*="css"] { font-family: 'Chakra Petch', sans-serif !important; background-color: #0B0F14; }
    .titulo-app { font-family: 'Orbitron', sans-serif; font-size: 2.2rem; font-weight: 900; color: #39FF88; text-shadow: 0 0 10px rgba(57, 255, 136, 0.4); margin-bottom: 2px; }
    .subtitulo-app { color: #A9F5D6; font-size: 1.1rem; margin-bottom: 20px; }
    div[data-testid="stWidgetLabel"] p { color: #5CF2C2 !important; font-weight: 600; }
    .alerta-baja { background-color: #FF3B5C; color: white; padding: 6px; border-radius: 4px; font-weight: bold; text-align: center; }
    .stock-ok { background-color: #28a745; color: white; padding: 6px; border-radius: 4px; font-weight: bold; text-align: center; }
    </style>
    """,
    unsafe_allow_html=True
)

st.markdown(f'<div class="titulo-app">⚡ {NOMBRE_APP}</div>', unsafe_allow_html=True)
st.markdown(f'<div class="subtitulo-app">{SUBTITULO_APP}</div>', unsafe_allow_html=True)

df_insp = cargar_inspecciones()
df_inv = cargar_inventario()

pestana1, pestana2, pestana3 = st.tabs(["📋 Verificación de Daños y Servicio", "📦 Inventario de Taller", "📊 Reportes y Alertas de Stock"])

# ----------------------------------------------------------------------------
# PESTAÑA 1: VERIFICACIÓN DE DAÑOS Y REGISTRO DE SERVICIOS
# ----------------------------------------------------------------------------
with pestana1:
    st.markdown("##### Registrar Reporte de Falla y Material Usado")
    
    with st.form("form_inspeccion", clear_on_submit=True):
        col1, col2 = st.columns(2)
        with col1:
            tipo_maq = st.selectbox("Equipo Intervenido", TIPOS_MAQUINA)
            id_maq = st.text_input("Identificador del Equipo (Ej: CH-04, TR-02)", placeholder="Código interno")
            cat = st.selectbox("Categoría del Daño", CATEGORIAS)
            comp = st.text_input("Componente Específico Afectado", placeholder="Ej: Alternador, Sensor de Presión")
        with col2:
            est = st.radio("Condición Final del Equipo", ESTADOS, horizontal=True)
            
            # Vinculación directa con el inventario existente
            materiales_disponibles = ["Ninguno / No requirió repuesto"] + df_inv["nombre_material"].tolist()
            mat_usado = st.selectbox("Repuesto utilizado del Inventario", materiales_disponibles)
            cant_usada = st.number_input("Cantidad de repuestos usados en la reparación", min_value=0, step=1, value=0)
            tecnico = st.text_input("Encargado de Verificación", value="Cristian Rubio")
            
        obs = st.text_area("Descripción detallada del daño / Solución técnica")
        enviar_insp = st.form_submit_button("Guardar Reporte y Descontar Stock")
        
        if enviar_insp:
            if not id_maq or not comp:
                st.error("Por favor completa el Identificador de la máquina y el Componente afectado.")
            elif mat_usado != "Ninguno / No requirió repuesto" and cant_usada <= 0:
                st.error("Si seleccionaste un repuesto, la cantidad utilizada debe ser mayor a 0.")
            else:
                proceder = True
                # Si usó material, verificar si hay stock suficiente en el taller antes de descontar
                if mat_usado != "Ninguno / No requirió repuesto":
                    stock_actual = int(df_inv.loc[df_inv["nombre_material"] == mat_usado, "cantidad_disponible"].values[0])
                    if cant_usada > stock_actual:
                        st.error(f"❌ No se puede registrar el servicio. Stock insuficiente en taller de {mat_usado}. Solo quedan {stock_actual} unidades.")
                        proceder = False
                    else:
                        # Descontar del inventario
                        df_inv.loc[df_inv["nombre_material"] == mat_usado, "cantidad_disponible"] = str(stock_actual - cant_usada)
                        guardar_inventario(df_inv)
                
                if proceder:
                    nuevo_id = siguiente_id(df_insp)
                    nueva_fila = {
                        "id": str(nuevo_id),
                        "fecha": date.today().strftime("%Y-%m-%d"),
                        "hora": datetime.now().strftime("%H:%M"),
                        "tipo_maquina": tipo_maq,
                        "identificador": id_maq.upper(),
                        "categoria": cat,
                        "componente": comp,
                        "estado": est,
                        "material_usado": mat_usado,
                        "cantidad_usada": str(cant_usada),
                        "observaciones": obs,
                        "tecnico": tecnico
                    }
                    df_insp = pd.concat([df_insp, pd.DataFrame([nueva_fila])], ignore_index=True)
                    guardar_inspecciones(df_insp)
                    st.success(f"✔️ Reporte #{nuevo_id} guardado. Inventario de taller actualizado automáticamente.")

    if not df_insp.empty:
        st.markdown("##### Historial de Reparaciones Realizadas")
        st.dataframe(df_insp.tail(10), use_container_width=True)

# ----------------------------------------------------------------------------
# PESTAÑA 2: INVENTARIO DE TALLER (CONTROL TOTAL PARA TI Y TU JEFE)
# ----------------------------------------------------------------------------
with pestana2:
    st.markdown("##### Repuestos y Materiales Físicos en el Taller Eléctrico")
    
    # Vista limpia del inventario para monitoreo del Jefe
    if not df_inv.empty:
