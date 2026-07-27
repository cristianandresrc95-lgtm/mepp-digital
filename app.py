"""
==================================================================================
 APP: INCAVOLT - Mantenimiento Eléctrico Preventivo y Predictivo
 Ingenio Incauca
 Alcance: Cosechadoras John Deere y Tractores de Alce (equipos en Standby)
 Desarrollado por: Cristian Rubio · Electricista de Cosechadoras y Tractores
 (código generado con apoyo de Claude/Anthropic como herramienta de soporte)
==================================================================================

Cómo ejecutar:
    1) pip install streamlit pandas plotly
    2) streamlit run app.py

El prototipo persiste los datos en tres archivos CSV locales
(inspecciones.csv, stock_repuestos.csv e inventario_taller.csv) ubicados junto a este script,
para que la información no se pierda al cerrar el navegador.
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
    """Inserta manifest.json y meta-tags en el head para el comportamiento tipo PWA."""
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
# CAPA DE DATOS
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


def cargar_stock() -> pd.DataFrame:
    _crear_archivo_si_no_existe(ARCHIVO_STOCK, COLUMNAS_STOCK)
    df = pd.read_csv(ARCHIVO_STOCK, dtype=str).fillna("")
    return df


def guardar_stock(df: pd.DataFrame):
    df.to_csv(ARCHIVO_STOCK, index=False)


def cargar_inventario() -> pd.DataFrame:
    _crear_archivo_si_no_existe(ARCHIVO_INVENTARIO, COLUMNAS_INVENTARIO)
    df = pd.read_csv(ARCHIVO_INVENTARIO, dtype=str).fillna("")
    if df.empty or "part_number" not in df.columns:
        datos_iniciales = [
            {"repuesto_id": "1", "nombre_material": "Sensor RPM John Deere", "part_number": "RE519144", "categoria": "Sensor", "cantidad_disponible": "12", "costo_unitario_cop": "320000", "ubicacion_estante": "Estante A-1", "alerta_minimo": "2"},
            {"repuesto_id": "2", "nombre_material": "Relé 5 Pines 12V Heavy Duty", "part_number": "AR27401", "categoria": "Relé", "cantidad_disponible": "30", "costo_unitario_cop": "45000", "ubicacion_estante": "Estante B-3", "alerta_minimo": "5"},
            {"repuesto_id": "3", "nombre_material": "Fusible 15A Tipo Ficha", "part_number": "AT146055", "categoria": "Fusible", "cantidad_disponible": "100", "costo_unitario_cop": "3500", "ubicacion_estante": "Gaveta C-1", "alerta_minimo": "10"},
            {"repuesto_id": "4", "nombre_material": "Electrovalvula de Alce Tractor Game", "part_number": "GAME-E04", "categoria": "Electrovalvula", "cantidad_disponible": "6", "costo_unitario_cop": "850000", "ubicacion_estante": "Estante D-2", "alerta_minimo": "1"},
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
# ESTILOS ORIGINALES
# ----------------------------------------------------------------------------
st.markdown(
    """
    <style>
    @import url('https://googleapis.com');

    html, body, [class*="css"] {
        font-family: 'Chakra Petch', sans-serif !important;
        font-size: 1.12rem;
    }

    div[data-testid="stAppViewContainer"] {
        background-color: #0B0F14;
    }
    section[data-testid="stSidebar"] > div {
        background-color: #0E1218;
    }
    div[data-testid="stHeader"] { background: rgba(0,0,0,0); }

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

    div[data-testid="stCaptionContainer"], div[data-testid="stCaptionContainer"] p {
        font-size: 1.08rem !important;
        color: #A9F5D6 !important;
        font-weight: 500 !important;
        letter-spacing: 0.2px;
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


