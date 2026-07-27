"""
==================================================================================
 APP: INCAVOLT - Mantenimiento Eléctrico Preventivo y Control de Costos
 Ingenio Incauca
 Alcance: Cosechadoras John Deere/Case y Tractores Game (equipos en Standby)
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


def inyectar_pwa():
    """Inserta manifest.json y meta-tags en el <head> para que, al agregar
    la app a la pantalla de inicio del celular, se abra en pantalla completa."""
    components.html(
        """
        <script>
        (function () {
            const parentDoc = window.parent.document;
            function addTag(tag, attrs) {
                const selector = tag + '[data-incavolt="true"]' +
                    Object.entries(attrs).map(([k, v]) => `[${k}="${v}"]`).join('');
                if (parentDoc.querySelector(selector)) return;
                const el = parentDoc.createElement(tag);
                el.setAttribute('data-incavolt', 'true');
                for (const [k, v] of Object.entries(attrs)) el.setAttribute(k, v);
                parentDoc.head.appendChild(el);
            }
            addTag('link', {rel: 'manifest', href: 'app/static/manifest.json'});
            addTag('link', {rel: 'apple-touch-icon', href: 'app/static/apple-touch-icon.png'});
            addTag('meta', {name: 'theme-color', content: '#0B0F14'});
            addTag('meta', {name: 'apple-mobile-web-app-capable', content: 'yes'});
            addTag('meta', {name: 'apple-mobile-web-app-status-bar-style', content: 'black-translucent'});
            addTag('meta', {name: 'apple-mobile-web-app-title', content: 'IncaVolt'});
        })();
        </script>
        """,
        height=0,
        width=0,
    )


inyectar_pwa()

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
ARCHIVO_INSPECCIONES = os.path.join(BASE_DIR, "inspecciones.csv")
ARCHIVO_INVENTARIO = os.path.join(BASE_DIR, "inventario_taller.csv")

COLUMNAS_INSPECCION = [
    "id", "fecha", "hora", "tipo_maquina", "identificador", "categoria",
    "componente", "estado", "material_usado", "cantidad_usada", "costo_total_servicio", "observaciones", "tecnico",
]

COLUMNAS_INVENTARIO = [
    "repuesto_id", "nombre_material", "part_number", "categoria", "cantidad_disponible", "costo_unitario_cop", "ubicacion_estante", "alerta_minimo"
]

CATEGORIAS = ["Sensor", "Relé", "Fusible", "Cableado / Ramal", "Luces / Señalización", "Bobina", "Electrovalvula", "Otro"]
TIPOS_MAQUINA = ["Cosechadora John Deere", "Cosechadora Case", "Tractor Game"]
ESTADOS = ["Verde", "Amarillo", "Rojo"]

ESTADO_INFO = {
    "Verde":    {"emoji": "🟢", "label": "Operativo",  "color": "#39FF88", "desc": "Componente en condición normal, sin novedad."},
    "Amarillo": {"emoji": "🟡", "label": "Alerta",     "color": "#FFD60A", "desc": "Puede continuar operando bajo monitoreo preventivo."},
    "Rojo":     {"emoji": "🔴", "label": "Crítico",    "color": "#FF3B5C", "desc": "Requiere cambio o intervención urgente."},
}

# ----------------------------------------------------------------------------
# CAPA DE DATOS (CSV locales para el Ingenio)
# ----------------------------------------------------------------------------
def _crear_archivo_si_no_existe(ruta, columnas):
    if not os.path.exists(ruta):
        pd.DataFrame(columns=columnas).to_csv(ruta, index=False)


def cargar_inspecciones() -> pd.DataFrame:
    _crear_archivo_si_no_existe(ARCHIVO_INSPECCIONES, COLUMNAS_INSPECCION)
    df = pd.read_csv(ARCHIVO_INSPECCIONES, dtype=str).fillna("")
    return df


def guardar_inspecciones(df: pd.DataFrame):
    df.to_csv(ARCHIVO_INSPECCIONES, index=False)


def cargar_inventario() -> pd.DataFrame:
    _crear_archivo_si_no_existe(ARCHIVO_INVENTARIO, COLUMNAS_INVENTARIO)
    df = pd.read_csv(ARCHIVO_INVENTARIO, dtype=str).fillna("")
    if df.empty or "part_number" not in df.columns:
        datos_iniciales = [
            {"repuesto_id": "1", "nombre_material": "Sensor RPM John Deere", "part_number": "RE519144", "categoria": "Sensor", "cantidad_disponible": "10", "costo_unitario_cop": "320000", "ubicacion_estante": "A-1", "alerta_minimo": "2"},
            {"repuesto_id": "2", "nombre_material": "Relé 5 Pines 12V Heavy Duty", "part_number": "AR27401", "categoria": "Relé", "cantidad_disponible": "25", "costo_unitario_cop": "45000", "ubicacion_estante": "B-3", "alerta_minimo": "5"},
            {"repuesto_id": "3", "nombre_material": "Fusible 15A Tipo Ficha", "part_number": "AT146055", "categoria": "Fusible", "cantidad_disponible": "50", "costo_unitario_cop": "3500", "ubicacion_estante": "C-1", "alerta_minimo": "10"},
            {"repuesto_id": "4", "nombre_material": "Electrovalvula de Alce Tractor Game", "part_number": "GAME-E04", "categoria": "Electrovalvula", "cantidad_disponible": "4", "costo_unitario_cop": "850000", "ubicacion_estante": "D-2", "alerta_minimo": "1"},
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
# ESTILOS ORIGINALES DE TU APLICACIÓN (CORREGIDOS Y COMPLETADOS)
# ----------------------------------------------------------------------------
st.markdown(
    """
    <style>
    @import url('https://googleapis.com');

    html, body, [class*="css"] {
        font-family: 'Chakra Petch', sans-serif !important;
        font-size: 1.12rem;
    }

    /* Trasfondo general con patrón de circuito */
    div[data-testid="stAppViewContainer"] {
        background-color: #0B0F14;
    }
    div[data-testid="stHeader"] { background: rgba(0,0,0,0); }

    /* Títulos principales */
    .titulo-app {
        font-family: 'Orbitron', sans-serif;
        font-size: 2.5rem;
        font-weight: 900;
        letter-spacing: 1px;
        color: #39FF88;
        text-shadow: 0 0 14px rgba(57, 255, 136, 0.55), 0 0 2px rgba(57,255,136,0.8);
        margin-bottom: 2px;
    }
    .subtitulo-app {
        font-family: 'Chakra Petch', sans-serif;
        color: #A9F5D6;
        margin-top: 0px;
        font-size: 1.25rem;
        font-weight: 600;
        letter-spacing: 0.4px;
        margin-bottom: 25px;
    }

    /* Encabezados de sección */
    h4, h5, h6 {
        font-family: 'Orbitron', sans-serif !important;
        color: #5CF2C2 !important;
        letter-spacing: 0.6px;
        font-size: 1.4rem !important;
        text-shadow: 0 0 8px rgba(92, 242, 194, 0.35);
        margin-top: 15px !important;
    }

    div[data-testid="stMarkdownContainer"] p {
        font-size: 1.14rem;
        line-height: 1.55;
    }

    div[data-testid="stWidgetLabel"] p, div[data-testid="stWidgetLabel"] label {
        color: #5CF2C2 !important;
        font-weight: 600 !important;
    }

    .card-estado {
        padding: 15px;
        border-radius: 8px;
        margin-bottom: 12px;
        border: 1px solid #233342;
    }
    .metrica-card {
        background-color: #121820;
        padding: 20px;
        border-radius: 8px;
        border: 1px solid #233342;
        text-align: center;
    }
    .alerta-baja {
        background-color: #FF3B5C;
        color: white;
        padding: 10px;
        border-radius: 6px;
        font-weight: bold;
        margin-bottom: 8px;
    }
    .stock-ok {
        background-color: #28a745;
        color: white;
        padding: 10px;
        border-radius: 6px;
        font-weight: bold;
        text-align: center;
    }
    </style>
    """,
    unsafe_allow_html=True
)

# ----------------------------------------------------------------------------
# INTERFAZ DE USUARIO ORIGINAL
# ----------------------------------------------------------------------------
st.markdown(f'<div class="titulo-app">⚡ {NOMBRE_APP}</div>', unsafe_allow_html=True)
st.markdown(f'<div class="subtitulo-app">{SUBTITULO_APP} · Desarrollado por {DESARROLLADOR}</div>', unsafe_allow_html=True)

df_insp = cargar_inspecciones()
df_inv = cargar_inventario()

# Estructura limpia de pestañas para celular
pestana1, pestana2, pestana3 = st.tabs(["📋 Verificación de Daños", "📦 Inventario de Taller", "📊 Reportes y Alertas"])

# PESTAÑA 1: VERIFICACIÓN DE DAÑOS
with pestana1:
    st.markdown("##### Registrar Reporte Eléctrico de Campo")
    
    with st.form("form_inspeccion", clear_on_submit=True):
        col1, col2 = st.columns(2)
        with col1:
            tipo_maq = st.selectbox("Equipo", TIPOS_MAQUINA)
            id_maq = st.text_input("Identificador (Ej: CH-04, TR-12)", placeholder="Escribe el código")
            cat = st.selectbox("Categoría del Componente", CATEGORIAS)
