"""
==================================================================================
 APP: INCAVOLT - Mantenimiento Eléctrico Preventivo y Control de Costos
 Ingenio Incauca
 Alcance: Cosechadoras John Deere y Tractores de Alce (equipos en Standby)
 Desarrollado por: Cristian Rubio · Electricista de Cosechadoras y Tractores
 (código generado con apoyo de Claude/Anthropic como herramienta de soporte)
==================================================================================

Cómo ejecutar:
    1) pip install streamlit pandas plotly
    2) streamlit run app.py
"""

import os
from datetime import datetime, date
import pandas as pd
import plotly.express as px
import streamlit as st

# ----------------------------------------------------------------------------
# MARCA DE LA APLICACIÓN ORIGINAL
# ----------------------------------------------------------------------------
NOMBRE_APP = "IncaVolt"
SUBTITULO_APP = "Mantenimiento Eléctrico Preventivo · Incauca"
DESARROLLADOR = "(Cristian Rubio) · Encargado de Electricidad de Cosechadoras"

# ----------------------------------------------------------------------------
# CONFIGURACIÓN GENERAL
# ----------------------------------------------------------------------------
st.set_page_config(
    page_title=f"{NOMBRE_APP} | Mantenimiento Eléctrico Preventivo",
    page_icon="⚡",
    layout="wide",
    initial_sidebar_state="expanded",
)

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
ARCHIVO_INSPECCIONES = os.path.join(BASE_DIR, "inspecciones.csv")
ARCHIVO_STOCK = os.path.join(BASE_DIR, "stock_repuestos.csv")
ARCHIVO_INVENTARIO = os.path.join(BASE_DIR, "inventario_taller.csv")

COLUMNAS_INSPECCION = [
    "id", "fecha", "hora", "tipo_maquina", "identificador", "categoria",
    "componente", "estado", "material_usado", "cantidad_usada", "costo_total_servicio", "observaciones", "tecnico",
]

COLUMNAS_STOCK = [
    "id", "fecha_solicitud", "repuesto", "cantidad", "prioridad",
    "origen_maquina", "componente_relacionado", "estado_stock", "notas",
]

COLUMNAS_INVENTARIO = [
    "repuesto_id", "nombre_material", "part_number", "categoria", "cantidad_disponible", "costo_unitario_cop", "ubicacion_estante", "alerta_minimo"
]

CATEGORIAS = ["Sensor", "Relé", "Fusible", "Cableado / Ramal", "Luces / Señalización", "Bobina", "Electrovalvula", "Luces", "Otro"]
TIPOS_MAQUINA = ["Cosechadora John Deere", "Cosechadora Case", "Tractor Game"]
ESTADOS = ["Verde", "Amarillo", "Rojo"]

ESTADO_INFO = {
    "Verde":    {"emoji": "🟢", "label": "Operativo",  "color": "#39FF88", "desc": "Componente en condición normal, sin novedad."},
    "Amarillo": {"emoji": "🟡", "label": "Alerta",     "color": "#FFD60A", "desc": "Puede continuar operando bajo monitoreo preventivo."},
    "Rojo":     {"emoji": "🔴", "label": "Crítico",    "color": "#FF3B5C", "desc": "Requiere cambio o intervención urgente."},
}

PRIORIDADES = ["Alta", "Media", "Baja"]
ESTADOS_STOCK = ["Pendiente por solicitar", "Solicitado a bodega", "Recibido / Listo en stock"]

# ----------------------------------------------------------------------------
# CAPA DE DATOS BASE
# ----------------------------------------------------------------------------
def _crear_archivo_si_no_existe(ruta, columnas):
    if not os.path.exists(ruta):
        pd.DataFrame(columns=columnas).to_csv(ruta, index=False)

def cargar_inspecciones() -> pd.DataFrame:
    _crear_archivo_si_no_existe(ARCHIVO_INSPECCIONES, COLUMNAS_INSPECCION)
    return pd.read_csv(ARCHIVO_INSPECCIONES, dtype=str).fillna("")

def guardar_inspecciones(df: pd.DataFrame):
    df.to_csv(ARCHIVO_INSPECCIONES, index=False)

def cargar_stock() -> pd.DataFrame:
    _crear_archivo_si_no_existe(ARCHIVO_STOCK, COLUMNAS_STOCK)
    return pd.read_csv(ARCHIVO_STOCK, dtype=str).fillna("")

def guardar_stock(df: pd.DataFrame):
    df.to_csv(ARCHIVO_STOCK, index=False)

def cargar_inventario() -> pd.DataFrame:
    _crear_archivo_si_no_existe(ARCHIVO_INVENTARIO, COLUMNAS_INVENTARIO)
    df = pd.read_csv(ARCHIVO_INVENTARIO, dtype=str).fillna("")
    if df.empty or "part_number" not in df.columns:
        datos_iniciales = [
            {"repuesto_id": "1", "nombre_material": "Sensor RPM John Deere", "part_number": "RE519144", "categoria": "Sensor", "cantidad_disponible": "15", "costo_unitario_cop": "320000", "ubicacion_estante": "Estante A-1", "alerta_minimo": "2"},
            {"repuesto_id": "2", "nombre_material": "Relé 5 Pines 12V Heavy Duty", "part_number": "AR27401", "categoria": "Relé", "cantidad_disponible": "35", "costo_unitario_cop": "45000", "ubicacion_estante": "Estante B-3", "alerta_minimo": "5"},
            {"repuesto_id": "3", "nombre_material": "Fusible 15A Tipo Ficha", "part_number": "AT146055", "categoria": "Fusible", "cantidad_disponible": "120", "costo_unitario_cop": "3500", "ubicacion_estante": "Gaveta C-1", "alerta_minimo": "10"},
            {"repuesto_id": "4", "nombre_material": "Electrovalvula de Alce Tractor Game", "part_number": "GAME-E04", "categoria": "Electrovalvula", "cantidad_disponible": "8", "costo_unitario_cop": "850000", "ubicacion_estante": "Estante D-2", "alerta_minimo": "1"},
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
# ESTILOS VISUALES COMPLETO NEÓN
# ----------------------------------------------------------------------------
st.markdown(
    """
    <style>
    @import url('https://googleapis.com');
    html, body, [class*="css"] { font-family: 'Chakra Petch', sans-serif !important; font-size: 1.12rem; }
    div[data-testid="stAppViewContainer"] { background-color: #0B0F14; }
    .titulo-app { font-family: 'Orbitron', sans-serif; font-size: 2.5rem; font-weight: 900; color: #39FF88; text-shadow: 0 0 14px rgba(57, 255, 136, 0.55); margin-bottom: 2px; }
    .subtitulo-app { color: #A9F5D6; font-size: 1.25rem; font-weight: 600; margin-bottom: 25px; }
    div[data-testid="stWidgetLabel"] p { color: #5CF2C2 !important; font-weight: 600 !important; }
    .metrica-card { background-color: #121820; padding: 15px; border-radius: 8px; border: 1px solid #233342; text-align: center; }
    .alerta-baja { background-color: #FF3B5C; color: white; padding: 10px; border-radius: 6px; font-weight: bold; margin-bottom: 8px; }
    .stock-ok { background-color: #28a745; color: white; padding: 10px; border-radius: 6px; font-weight: bold; text-align: center; }
    </style>
    """,
    unsafe_allow_html=True
)

st.markdown(f'<div class="titulo-app">⚡ {NOMBRE_APP}</div>', unsafe_allow_html=True)
st.markdown(f'<div class="subtitulo-app">{SUBTITULO_APP} · {DESARROLLADOR}</div>', unsafe_allow_html=True)

df_insp = cargar_inspecciones()
df_stk = cargar_stock()
df_inv = cargar_inventario()

# Tus 3 pestañas originales del menú principal
pestana1, pestana2, pestana3 = st.tabs(["📋 Inspecciones y Uso", "📦 Inventario de Taller", "🔧 Stock / Pedidos y Jefatura"])

# PESTAÑA 1: INSPECCIONES
with pestana1:
    st.markdown("##### Registrar Reporte Eléctrico de Campo")
    with st.form("form_inspeccion", clear_on_submit=True):
        col1, col2 = st.columns(2)
        with col1:
            tipo_maq = st.selectbox("Equipo", TIPOS_MAQUINA)
            id_maq = st.text_input("Identificador (Ej: CH-04, TR-12)")
            cat = st.selectbox("Categoría del Componente", CATEGORIAS)
            comp = st.text_input("Componente Específico")
        with col2:
            est = st.radio("Estado de Condición", ESTADOS, horizontal=True)
            opciones_select = ["Ninguno / No requirió repuesto"] + df_inv["nombre_material"].tolist()
            seleccion_raw = st.selectbox("Material del Taller Utilizado", opciones_select)
            cant_usada = st.number_input("Cantidad Utilizada en Reparación", min_value=0, step=1, value=0)
            tecnico = st.text_input("Técnico Encargado", value="Cristian Rubio")
            
        obs = st.text_area("Observaciones / Novedad en campo")
        enviar_insp = st.form_submit_button("Guardar Inspección en Local")
        
        if enviar_insp:
            if not id_maq or not comp:
                st.error("Por favor completa el Identificador y el Componente.")
            else:
                proceder = True
                costo_total = 0
                if seleccion_raw != "Ninguno / No requirió repuesto" and cant_usada > 0:
                    stock_actual = int(df_inv.loc[df_inv["nombre_material"] == seleccion_raw, "cantidad_disponible"].values[0])
                    costo_u = float(df_inv.loc[df_inv["nombre_material"] == seleccion_raw, "costo_unitario_cop"].values[0])
                    costo_total = costo_u * cant_usada
                    if cant_usada > stock_actual:
                        st.error(f"❌ Stock insuficiente. Solo quedan {stock_actual} unidades.")
                        proceder = False
                    else:
                        df_inv.loc[df_inv["nombre_material"] == seleccion_raw, "cantidad_disponible"] = str(stock_actual - cant_usada)
                        guardar_inventario(df_inv)
                
                if proceder:
                    nuevo_id = siguiente_id(df_insp)
                    nueva_fila = {
                        "id": str(nuevo_id), "fecha": date.today().strftime("%Y-%m-%d"), "hora": datetime.now().strftime("%H:%M"),
                        "tipo_maquina": tipo_maq, "identificador": id_maq.upper(), "categoria": cat, "componente": comp, "estado": est,
