"""
==================================================================================
 APP: INCAVOLT - Mantenimiento Eléctrico Preventivo y Predictivo
 Ingenio Incauca
 Alcance: Cosechadoras John Deere y Tractores de Alce (equipos en Standby)
 Desarrollado por: [Tu Nombre] · Electricista de Cosechadoras y Tractores
 (código generado con apoyo de Claude/Anthropic como herramienta de soporte)
==================================================================================

Cómo ejecutar:
    1) pip install streamlit pandas plotly
    2) streamlit run app.py

El prototipo persiste los datos en dos archivos CSV locales
(inspecciones.csv y stock_repuestos.csv) ubicados junto a este script,
para que la información no se pierda al cerrar el navegador.
Para producción real, reemplazar la capa CSV por una base de datos
(SQLite / PostgreSQL) sin cambiar el resto del código.
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
DESARROLLADOR = "[Tu Nombre] · Electricista de Cosechadoras y Tractores"

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
    la app a la pantalla de inicio del celular, se abra en pantalla completa
    con ícono y nombre propios (comportamiento tipo app nativa / PWA)."""
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
ARCHIVO_INVENTARIO = os.path.join(BASE_DIR, "inventario.csv")
ARCHIVO_MOVIMIENTOS = os.path.join(BASE_DIR, "movimientos_inventario.csv")
ARCHIVO_PRESUPUESTO = os.path.join(BASE_DIR, "presupuesto_maquinas.csv")

COLUMNAS_INSPECCION = [
    "id", "fecha", "hora", "tipo_maquina", "identificador", "categoria",
    "componente", "estado", "observaciones", "tecnico",
    "ejecutado", "fecha_ejecucion",
]

COLUMNAS_STOCK = [
    "id", "fecha_solicitud", "repuesto", "cantidad", "prioridad",
    "origen_maquina", "componente_relacionado", "estado_stock", "notas",
]

COLUMNAS_INVENTARIO = [
    "id", "material", "categoria", "unidad", "cantidad_actual",
    "cantidad_minima", "costo_unitario", "ubicacion", "notas",
]

COLUMNAS_MOVIMIENTOS = [
    "id", "fecha", "tipo_movimiento", "material", "cantidad",
    "motivo", "inspeccion_id", "tecnico",
]

COLUMNAS_PRESUPUESTO = [
    "id", "identificador_maquina", "tipo_maquina", "periodo",
    "presupuesto_asignado", "notas",
]

CATEGORIAS = ["Sensor", "Relé", "Fusible", "Cableado / Ramal", "Luces / Señalización", "Otro"]
TIPOS_MAQUINA = ["Cosechadora John Deere", "Tractor de Alce"]
ESTADOS = ["Verde", "Amarillo", "Rojo"]

ESTADO_INFO = {
    "Verde":    {"emoji": "🟢", "label": "Operativo",  "color": "#39FF88", "desc": "Componente en condición normal, sin novedad."},
    "Amarillo": {"emoji": "🟡", "label": "Alerta",     "color": "#FFD60A", "desc": "Puede continuar operando bajo monitoreo preventivo."},
    "Rojo":     {"emoji": "🔴", "label": "Crítico",    "color": "#FF3B5C", "desc": "Requiere cambio o intervención urgente."},
}

PRIORIDADES = ["Alta", "Media", "Baja"]
ESTADOS_STOCK = ["Pendiente por solicitar", "Solicitado a bodega", "Recibido / Listo en stock"]
UNIDADES_MATERIAL = ["unidad(es)", "metro(s)", "rollo(s)", "caja(s)", "kit(s)"]


# ----------------------------------------------------------------------------
# CAPA DE DATOS (CSV como persistencia simple para el prototipo)
# ----------------------------------------------------------------------------
def _crear_archivo_si_no_existe(ruta, columnas):
    if not os.path.exists(ruta):
        pd.DataFrame(columns=columnas).to_csv(ruta, index=False)


def _asegurar_columnas(df: pd.DataFrame, columnas: list, valores_default: dict = None) -> pd.DataFrame:
    """Agrega columnas nuevas a archivos CSV antiguos que fueron creados
    antes de que existieran (evita romper datos ya guardados)."""
    valores_default = valores_default or {}
    for col in columnas:
        if col not in df.columns:
            df[col] = valores_default.get(col, "")
    return df[columnas]


def cargar_inspecciones() -> pd.DataFrame:
    _crear_archivo_si_no_existe(ARCHIVO_INSPECCIONES, COLUMNAS_INSPECCION)
    df = pd.read_csv(ARCHIVO_INSPECCIONES, dtype=str).fillna("")
    df = _asegurar_columnas(df, COLUMNAS_INSPECCION, {"ejecutado": "No"})
    return df


def guardar_inspecciones(df: pd.DataFrame):
    df.to_csv(ARCHIVO_INSPECCIONES, index=False)


def cargar_stock() -> pd.DataFrame:
    _crear_archivo_si_no_existe(ARCHIVO_STOCK, COLUMNAS_STOCK)
    df = pd.read_csv(ARCHIVO_STOCK, dtype=str).fillna("")
    df = _asegurar_columnas(df, COLUMNAS_STOCK)
    return df


def guardar_stock(df: pd.DataFrame):
    df.to_csv(ARCHIVO_STOCK, index=False)


def cargar_inventario() -> pd.DataFrame:
    _crear_archivo_si_no_existe(ARCHIVO_INVENTARIO, COLUMNAS_INVENTARIO)
    df = pd.read_csv(ARCHIVO_INVENTARIO, dtype=str).fillna("")
    df = _asegurar_columnas(df, COLUMNAS_INVENTARIO, {"costo_unitario": "0"})
    return df


def guardar_inventario(df: pd.DataFrame):
    df.to_csv(ARCHIVO_INVENTARIO, index=False)


def cargar_movimientos() -> pd.DataFrame:
    _crear_archivo_si_no_existe(ARCHIVO_MOVIMIENTOS, COLUMNAS_MOVIMIENTOS)
    df = pd.read_csv(ARCHIVO_MOVIMIENTOS, dtype=str).fillna("")
    df = _asegurar_columnas(df, COLUMNAS_MOVIMIENTOS)
    return df


def guardar_movimientos(df: pd.DataFrame):
    df.to_csv(ARCHIVO_MOVIMIENTOS, index=False)


def cargar_presupuesto() -> pd.DataFrame:
    _crear_archivo_si_no_existe(ARCHIVO_PRESUPUESTO, COLUMNAS_PRESUPUESTO)
    df = pd.read_csv(ARCHIVO_PRESUPUESTO, dtype=str).fillna("")
    df = _asegurar_columnas(df, COLUMNAS_PRESUPUESTO)
    return df


def guardar_presupuesto(df: pd.DataFrame):
    df.to_csv(ARCHIVO_PRESUPUESTO, index=False)


def siguiente_id(df: pd.DataFrame) -> int:
    if df.empty:
        return 1
    return int(pd.to_numeric(df["id"], errors="coerce").fillna(0).max()) + 1


# ----------------------------------------------------------------------------
# ESTILOS
# ----------------------------------------------------------------------------
st.markdown(
    """
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Orbitron:wght@600;800;900&family=Chakra+Petch:wght@400;500;600;700&display=swap');

    html, body, [class*="css"] {
        font-family: 'Chakra Petch', sans-serif !important;
        font-size: 1.12rem;
    }

    /* ---------- Trasfondo general con patrón de circuito ---------- */
    div[data-testid="stAppViewContainer"] {
        background-color: #0B0F14;
        background-image: url('app/static/bg-circuit.svg');
        background-repeat: repeat;
        background-size: 240px 240px;
    }
    section[data-testid="stSidebar"] > div {
        background-color: #0E1218;
        background-image: url('app/static/bg-circuit.svg');
        background-repeat: repeat;
        background-size: 240px 240px;
    }
    div[data-testid="stHeader"] { background: rgba(0,0,0,0); }

    /* ---------- Títulos principales ---------- */
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
    }

    /* ---------- Encabezados de sección (##### en st.markdown) ---------- */
    h4, h5, h6 {
        font-family: 'Orbitron', sans-serif !important;
        color: #5CF2C2 !important;
        letter-spacing: 0.6px;
        font-size: 1.4rem !important;
        text-shadow: 0 0 8px rgba(92, 242, 194, 0.35);
    }

    /* ---------- Texto general de párrafos / markdown ---------- */
    div[data-testid="stMarkdownContainer"] p {
        font-size: 1.14rem;
        line-height: 1.55;
    }

    /* ---------- Descripciones (st.caption) ---------- */
    div[data-testid="stCaptionContainer"], div[data-testid="stCaptionContainer"] p {
        font-size: 1.08rem !important;
        color: #A9F5D6 !important;
        font-weight: 500 !important;
        letter-spacing: 0.2px;
    }

    /* ---------- Etiquetas de campos (labels de inputs/selects) ---------- */
    div[data-testid="stWidgetLabel"] p, div[data-testid="stWidgetLabel"] label {
        font-family: 'Chakra Petch', sans-serif !important;
        font-size: 1.18rem !important;
        font-weight: 600 !important;
        color: #D6FFF0 !important;
        letter-spacing: 0.3px;
    }

    /* ---------- Opciones del menú de navegación (radio lateral) ---------- */
    section[data-testid="stSidebar"] div[role="radiogroup"] label p {
        font-family: 'Chakra Petch', sans-serif !important;
        font-size: 1.35rem !important;
        font-weight: 700 !important;
        color: #EAFFF6 !important;
        letter-spacing: 0.3px;
    }
    section[data-testid="stSidebar"] div[role="radiogroup"] label {
        padding: 6px 0;
    }

    /* ---------- Texto dentro de tablas / data editor ---------- */
    div[data-testid="stDataFrame"] * , div[data-testid="stTable"] * {
        font-size: 1.02rem !important;
    }

    /* ---------- Badges de estado (semáforo) ---------- */
    .badge {
        display: inline-block;
        padding: 6px 18px;
        border-radius: 20px;
        color: #05100A;
        font-family: 'Orbitron', sans-serif;
        font-weight: 700;
        font-size: 1.1rem;
        text-align: center;
        box-shadow: 0 0 16px currentColor;
    }

    /* ---------- Tarjetas KPI tipo panel futurista ---------- */
    .card-kpi {
        position: relative;
        border-radius: 16px;
        padding: 28px 18px;
        text-align: center;
        background: linear-gradient(160deg, rgba(255,255,255,0.07), rgba(255,255,255,0.015));
        border: 1px solid rgba(57, 255, 136, 0.35);
        box-shadow: 0 0 24px rgba(57, 255, 136, 0.15), inset 0 0 20px rgba(255,255,255,0.03);
        backdrop-filter: blur(6px);
    }
    .card-kpi h1 {
        margin: 0;
        font-family: 'Orbitron', sans-serif;
        font-size: 2.9rem;
        font-weight: 900;
        text-shadow: 0 0 18px currentColor;
    }
    .card-kpi p {
        margin: 8px 0 0 0;
        font-size: 1.08rem;
        font-weight: 600;
        letter-spacing: 0.4px;
        opacity: 0.95;
    }

    /* ---------- Contenedores generales (st.container(border=True)) ---------- */
    div[data-testid="stVerticalBlockBorderWrapper"] {
        border-radius: 14px !important;
        border: 1px solid rgba(57, 255, 136, 0.18) !important;
        background: rgba(255,255,255,0.025);
    }

    /* ---------- Botones ---------- */
    button[kind="primary"], .stButton>button, .stFormSubmitButton>button {
        font-family: 'Orbitron', sans-serif !important;
        letter-spacing: 0.5px;
        font-weight: 700 !important;
        font-size: 1.02rem !important;
        border-radius: 10px !important;
        border: 1px solid rgba(57, 255, 136, 0.5) !important;
        box-shadow: 0 0 14px rgba(57, 255, 136, 0.25);
    }

    /* ---------- Sidebar ---------- */
    section[data-testid="stSidebar"] {
        border-right: 1px solid rgba(57, 255, 136, 0.25);
    }
    section[data-testid="stSidebar"] h3 {
        font-family: 'Orbitron', sans-serif !important;
        color: #39FF88 !important;
        text-shadow: 0 0 10px rgba(57,255,136,0.5);
        font-size: 1.5rem !important;
    }

    /* ---------- Métricas nativas (st.metric) ---------- */
    div[data-testid="stMetricValue"] {
        font-family: 'Orbitron', sans-serif;
        font-size: 2rem;
        text-shadow: 0 0 10px rgba(57,255,136,0.35);
    }
    div[data-testid="stMetricLabel"] p {
        font-size: 1.05rem !important;
        color: #A9F5D6 !important;
    }
    </style>
    """,
    unsafe_allow_html=True,
)


def badge_estado(estado: str) -> str:
    info = ESTADO_INFO.get(estado, {"color": "#999", "emoji": "⚪", "label": estado})
    color = info["color"]
    return (
        f'<span class="badge" style="background-color:{color}; '
        f'box-shadow:0 0 16px {color};">{info["emoji"]} {info["label"]}</span>'
    )


# ----------------------------------------------------------------------------
# SIDEBAR / NAVEGACIÓN
# ----------------------------------------------------------------------------
with st.sidebar:
    col_logo, col_txt = st.columns([1, 3])
    with col_logo:
        if os.path.exists(os.path.join(BASE_DIR, "static", "icon-192.png")):
            st.image(os.path.join(BASE_DIR, "static", "icon-192.png"), width=48)
        else:
            st.markdown("### ⚡")
    with col_txt:
        st.markdown(f"### {NOMBRE_APP}")
    st.caption(SUBTITULO_APP)
    st.markdown("---")
    pagina = st.radio(
        "Ir a:",
        [
            "📋 Registrar Inspección",
            "🚦 Historial y Ejecución de OT",
            "📦 Inventario de Taller",
            "💰 Presupuesto por Máquina",
            "🔧 Repuestos por Comprar",
            "📊 Dashboard Supervisor",
        ],
    )
    st.markdown("---")
    st.caption("Ingenio Incauca | Área de Mantenimiento Eléctrico")
    st.caption("Flota: Cosechadoras John Deere y Tractores de Alce")
    st.caption(f"Sesión: {date.today().strftime('%d/%m/%Y')}")
    st.markdown("---")
    st.caption(f"👤 Desarrollado por {DESARROLLADOR}")

df_insp = cargar_inspecciones()
df_stock = cargar_stock()
df_inventario = cargar_inventario()
df_movimientos = cargar_movimientos()
df_presupuesto = cargar_presupuesto()


# ==============================================================================
# PÁGINA 1 · REGISTRAR INSPECCIÓN
# ==============================================================================
if pagina == "📋 Registrar Inspección":
    st.markdown('<p class="titulo-app">📋 Registro de Inspección Eléctrica Preventiva</p>', unsafe_allow_html=True)
    st.markdown(
        '<p class="subtitulo-app">Registra la revisión de sensores, relés, fusibles, cableados y luces '
        'en máquinas en standby o tractores quieteros.</p>',
        unsafe_allow_html=True,
    )
    st.markdown("---")

    with st.form("form_inspeccion", clear_on_submit=True):
        col1, col2, col3 = st.columns(3)
        with col1:
            fecha_insp = st.date_input("Fecha de inspección", value=date.today())
            tipo_maquina = st.selectbox("Tipo de máquina", TIPOS_MAQUINA)
        with col2:
            identificador = st.text_input(
                "Identificador de máquina",
                placeholder="Ej: Cosechadora CH-08 / Tractor Alce 03",
            )
            categoria = st.selectbox("Categoría del componente", CATEGORIAS)
        with col3:
            tecnico = st.text_input("Técnico responsable", placeholder="Nombre del tecnólogo")
            estado = st.radio(
                "Estado del componente",
                ESTADOS,
                format_func=lambda e: f'{ESTADO_INFO[e]["emoji"]} {e} — {ESTADO_INFO[e]["label"]}',
                horizontal=False,
            )

        componente = st.text_input(
            "Componente específico revisado",
            placeholder="Ej: Sensor de altura de corte, Relé de 40A arranque, Ramal sulfatado luces traseras",
        )
        observaciones = st.text_area(
            "Observaciones técnicas",
            placeholder="Describe el hallazgo, causa probable y recomendación.",
            height=90,
        )

        st.markdown("##### 🔧 ¿Este hallazgo requiere dejar un repuesto listo en stock?")
        col4, col5, col6 = st.columns(3)
        with col4:
            repuesto_necesario = st.text_input(
                "Repuesto necesario (dejar vacío si no aplica)",
                placeholder="Ej: Fusible 30A, Relé 40A, Terminal ojo 10mm",
            )
        with col5:
            cantidad_repuesto = st.number_input("Cantidad", min_value=0, value=0, step=1)
        with col6:
            prioridad_repuesto = st.selectbox("Prioridad de compra", PRIORIDADES)

        enviado = st.form_submit_button("✅ Guardar inspección", use_container_width=True)

    if enviado:
        if not identificador.strip() or not componente.strip() or not tecnico.strip():
            st.error("Por favor completa al menos: identificador de máquina, componente revisado y técnico responsable.")
        else:
            nuevo_id = siguiente_id(df_insp)
            nueva_fila = {
                "id": nuevo_id,
                "fecha": fecha_insp.strftime("%Y-%m-%d"),
                "hora": datetime.now().strftime("%H:%M"),
                "tipo_maquina": tipo_maquina,
                "identificador": identificador.strip(),
                "categoria": categoria,
                "componente": componente.strip(),
                "estado": estado,
                "observaciones": observaciones.strip(),
                "tecnico": tecnico.strip(),
            }
            df_insp = pd.concat([df_insp, pd.DataFrame([nueva_fila])], ignore_index=True)
            guardar_inspecciones(df_insp)

            mensaje = f"Inspección registrada correctamente — {ESTADO_INFO[estado]['emoji']} {estado}."

            if repuesto_necesario.strip():
                nuevo_id_stock = siguiente_id(df_stock)
                nueva_fila_stock = {
                    "id": nuevo_id_stock,
                    "fecha_solicitud": fecha_insp.strftime("%Y-%m-%d"),
                    "repuesto": repuesto_necesario.strip(),
                    "cantidad": int(cantidad_repuesto) if cantidad_repuesto else 1,
                    "prioridad": prioridad_repuesto,
                    "origen_maquina": f"{tipo_maquina} - {identificador.strip()}",
                    "componente_relacionado": componente.strip(),
                    "estado_stock": "Pendiente por solicitar",
                    "notas": "",
                }
                df_stock = pd.concat([df_stock, pd.DataFrame([nueva_fila_stock])], ignore_index=True)
                guardar_stock(df_stock)
                mensaje += f" Se agregó **{repuesto_necesario.strip()}** a la lista de repuestos pendientes."

            st.success(mensaje)


# ==============================================================================
# PÁGINA 2 · HISTORIAL DE ESTADOS
# ==============================================================================
elif pagina == "🚦 Historial y Ejecución de OT":
    st.markdown('<p class="titulo-app">🚦 Historial, Semáforo y Ejecución de Órdenes de Trabajo</p>', unsafe_allow_html=True)
    st.markdown(
        '<p class="subtitulo-app">Consulta todas las inspecciones registradas, actualiza el estado y '
        'confirma la ejecución de reparaciones descontando el material usado del inventario.</p>',
        unsafe_allow_html=True,
    )
    st.markdown("---")

    if df_insp.empty:
        st.info("Aún no hay inspecciones registradas. Ve a **Registrar Inspección** para crear la primera.")
    else:
        col_f1, col_f2, col_f3 = st.columns(3)
        with col_f1:
            filtro_tipo = st.multiselect("Filtrar por tipo de máquina", TIPOS_MAQUINA, default=TIPOS_MAQUINA)
        with col_f2:
            filtro_estado = st.multiselect("Filtrar por estado", ESTADOS, default=ESTADOS)
        with col_f3:
            filtro_categoria = st.multiselect("Filtrar por categoría", CATEGORIAS, default=CATEGORIAS)

        df_view = df_insp[
            df_insp["tipo_maquina"].isin(filtro_tipo)
            & df_insp["estado"].isin(filtro_estado)
            & df_insp["categoria"].isin(filtro_categoria)
        ].copy()

        df_view = df_view.sort_values("id", ascending=False)

        st.markdown(f"**{len(df_view)} registro(s) encontrado(s)**")

        for _, fila in df_view.iterrows():
            with st.container(border=True):
                c1, c2, c3 = st.columns([3, 5, 2])
                with c1:
                    st.markdown(f"**{fila['identificador']}**")
                    st.caption(f"{fila['tipo_maquina']} · {fila['categoria']}")
                with c2:
                    st.markdown(f"🔩 **{fila['componente']}**")
                    if fila["observaciones"]:
                        st.caption(fila["observaciones"])
                    st.caption(f"📅 {fila['fecha']} {fila['hora']} · 👤 {fila['tecnico']}")
                with c3:
                    st.markdown(badge_estado(fila["estado"]), unsafe_allow_html=True)
                    if fila.get("ejecutado") == "Sí":
                        st.caption(f"✅ Ejecutado {fila.get('fecha_ejecucion', '')}")
                    else:
                        st.caption("⏳ Pendiente de ejecución")

        st.markdown("---")
        st.markdown("##### ✏️ Actualizar estado de un registro existente")
        col_u1, col_u2, col_u3 = st.columns([2, 2, 1])
        with col_u1:
            opciones_id = df_insp.sort_values("id", ascending=False).apply(
                lambda r: f"#{r['id']} · {r['identificador']} · {r['componente']}", axis=1
            ).tolist()
            seleccion = st.selectbox("Selecciona el registro a actualizar", opciones_id) if opciones_id else None
        with col_u2:
            nuevo_estado = st.radio(
                "Nuevo estado", ESTADOS,
                format_func=lambda e: f'{ESTADO_INFO[e]["emoji"]} {e}',
                horizontal=True,
            )
        with col_u3:
            st.write("")
            st.write("")
            actualizar = st.button("Actualizar", use_container_width=True)

        if actualizar and seleccion:
            id_sel = int(seleccion.split("·")[0].replace("#", "").strip())
            df_insp.loc[df_insp["id"].astype(str) == str(id_sel), "estado"] = nuevo_estado
            guardar_inspecciones(df_insp)
            st.success(f"Estado del registro #{id_sel} actualizado a {ESTADO_INFO[nuevo_estado]['emoji']} {nuevo_estado}.")
            st.rerun()

        st.markdown("---")
        st.markdown("##### ✅ Confirmar ejecución de orden de trabajo y descontar material")
        st.caption(
            "Cuando termines una reparación, selecciona la OT, el material del inventario que usaste "
            "y la cantidad. Se descuenta automáticamente del inventario de taller."
        )

        if df_inventario.empty:
            st.warning(
                "Todavía no tienes materiales cargados en **📦 Inventario de Taller**. "
                "Registra primero tu inventario para poder descontar materiales aquí."
            )
        else:
            col_e1, col_e2, col_e3, col_e4 = st.columns([2.3, 2.2, 1, 1.2])
            with col_e1:
                opciones_ot = df_insp.sort_values("id", ascending=False).apply(
                    lambda r: f"#{r['id']} · {r['identificador']} · {r['componente']} · "
                              f"{'✅ Ejecutado' if r.get('ejecutado') == 'Sí' else '⏳ Pendiente'}",
                    axis=1,
                ).tolist()
                seleccion_ot = st.selectbox("Orden de trabajo (registro)", opciones_ot, key="sel_ot_confirmar")
            with col_e2:
                opciones_material = df_inventario.apply(
                    lambda r: f"{r['material']} (disp: {r['cantidad_actual']} {r['unidad']})", axis=1
                ).tolist()
                material_sel = st.selectbox("Material usado", opciones_material, key="sel_material_confirmar")
            with col_e3:
                cantidad_usada = st.number_input("Cantidad", min_value=1, value=1, step=1, key="cant_usada_confirmar")
            with col_e4:
                st.write("")
                st.write("")
                confirmar_ejecucion = st.button("✅ Descontar", use_container_width=True, key="btn_confirmar_ot")

            if confirmar_ejecucion and seleccion_ot and material_sel:
                id_ot = int(seleccion_ot.split("·")[0].replace("#", "").strip())
                nombre_material = material_sel.split(" (disp:")[0].strip()
                idx_candidatos = df_inventario[df_inventario["material"] == nombre_material].index

                if len(idx_candidatos) == 0:
                    st.error("No se encontró el material seleccionado en el inventario.")
                else:
                    idx_material = idx_candidatos[0]
                    stock_actual = float(pd.to_numeric(df_inventario.loc[idx_material, "cantidad_actual"], errors="coerce") or 0)

                    if cantidad_usada > stock_actual:
                        st.error(
                            f"No hay suficiente stock de '{nombre_material}'. "
                            f"Disponible: {stock_actual}. Registra una entrada en Inventario de Taller antes de descontar."
                        )
                    else:
                        # Descontar del inventario
                        df_inventario.loc[idx_material, "cantidad_actual"] = stock_actual - cantidad_usada
                        guardar_inventario(df_inventario)

                        # Registrar movimiento de salida
                        tecnico_ot_series = df_insp.loc[df_insp["id"].astype(str) == str(id_ot), "tecnico"]
                        tecnico_ot = tecnico_ot_series.values[0] if not tecnico_ot_series.empty else ""

                        nuevo_id_mov = siguiente_id(df_movimientos)
                        fila_mov = {
                            "id": nuevo_id_mov,
                            "fecha": date.today().strftime("%Y-%m-%d"),
                            "tipo_movimiento": "Salida",
                            "material": nombre_material,
                            "cantidad": cantidad_usada,
                            "motivo": f"Reparación OT #{id_ot}",
                            "inspeccion_id": id_ot,
                            "tecnico": tecnico_ot,
                        }
                        df_movimientos = pd.concat([df_movimientos, pd.DataFrame([fila_mov])], ignore_index=True)
                        guardar_movimientos(df_movimientos)

                        # Marcar la inspección como ejecutada
                        df_insp.loc[df_insp["id"].astype(str) == str(id_ot), "ejecutado"] = "Sí"
                        df_insp.loc[df_insp["id"].astype(str) == str(id_ot), "fecha_ejecucion"] = date.today().strftime("%Y-%m-%d")
                        guardar_inspecciones(df_insp)

                        unidad_material = df_inventario.loc[idx_material, "unidad"] or "unidad(es)"
                        st.success(
                            f"OT #{id_ot} confirmada. Se descontaron {cantidad_usada} {unidad_material} "
                            f"de '{nombre_material}' del inventario de taller."
                        )
                        st.rerun()

        with st.expander("⬇️ Exportar historial completo (CSV)"):
            st.download_button(
                "Descargar inspecciones.csv",
                data=df_insp.to_csv(index=False).encode("utf-8"),
                file_name="inspecciones_mepp.csv",
                mime="text/csv",
            )


# ==============================================================================
# PÁGINA 2.5 · INVENTARIO DE TALLER
# ==============================================================================
elif pagina == "📦 Inventario de Taller":
    st.markdown('<p class="titulo-app">📦 Inventario de Materiales del Taller Eléctrico</p>', unsafe_allow_html=True)
    st.markdown(
        '<p class="subtitulo-app">Control del stock físico de materiales eléctricos disponibles para '
        'reparaciones de cosechadoras y tractores de alce — visible para ti y para tu jefatura.</p>',
        unsafe_allow_html=True,
    )
    st.markdown("---")

    with st.expander("➕ Agregar nuevo material al inventario"):
        with st.form("form_nuevo_material", clear_on_submit=True):
            c1, c2, c3, c4 = st.columns(4)
            with c1:
                material_nuevo = st.text_input("Nombre del material", placeholder="Ej: Relé 40A 12V")
                categoria_nueva = st.selectbox("Categoría", CATEGORIAS, key="cat_nuevo_material")
            with c2:
                cantidad_inicial = st.number_input("Cantidad inicial en stock", min_value=0, value=0, step=1)
                unidad_nueva = st.selectbox("Unidad de medida", UNIDADES_MATERIAL)
            with c3:
                cantidad_minima = st.number_input("Cantidad mínima (alerta de stock bajo)", min_value=0, value=2, step=1)
                costo_unitario_nuevo = st.number_input("Costo unitario ($ COP)", min_value=0.0, value=0.0, step=1000.0)
            with c4:
                ubicacion_nueva = st.text_input("Ubicación en taller", placeholder="Ej: Estante B - Caja 3")
            notas_nuevo = st.text_input("Notas (opcional)")
            crear_material = st.form_submit_button("Agregar material al inventario", use_container_width=True)

        if crear_material:
            if not material_nuevo.strip():
                st.error("Escribe el nombre del material.")
            else:
                nuevo_id_inv = siguiente_id(df_inventario)
                fila_inv = {
                    "id": nuevo_id_inv,
                    "material": material_nuevo.strip(),
                    "categoria": categoria_nueva,
                    "unidad": unidad_nueva,
                    "cantidad_actual": int(cantidad_inicial),
                    "cantidad_minima": int(cantidad_minima),
                    "costo_unitario": float(costo_unitario_nuevo),
                    "ubicacion": ubicacion_nueva.strip(),
                    "notas": notas_nuevo.strip(),
                }
                df_inventario = pd.concat([df_inventario, pd.DataFrame([fila_inv])], ignore_index=True)
                guardar_inventario(df_inventario)

                if cantidad_inicial > 0:
                    nuevo_id_mov = siguiente_id(df_movimientos)
                    fila_mov = {
                        "id": nuevo_id_mov,
                        "fecha": date.today().strftime("%Y-%m-%d"),
                        "tipo_movimiento": "Entrada",
                        "material": material_nuevo.strip(),
                        "cantidad": int(cantidad_inicial),
                        "motivo": "Carga inicial de inventario",
                        "inspeccion_id": "",
                        "tecnico": "",
                    }
                    df_movimientos = pd.concat([df_movimientos, pd.DataFrame([fila_mov])], ignore_index=True)
                    guardar_movimientos(df_movimientos)

                st.success(f"'{material_nuevo.strip()}' agregado al inventario con {int(cantidad_inicial)} {unidad_nueva}.")
                st.rerun()

    with st.expander("📥 Registrar entrada de material (compra recibida en bodega)"):
        if df_inventario.empty:
            st.info("Agrega primero al menos un material arriba.")
        else:
            with st.form("form_entrada_material", clear_on_submit=True):
                col_i1, col_i2, col_i3 = st.columns(3)
                with col_i1:
                    material_entrada = st.selectbox("Material", df_inventario["material"].tolist(), key="material_entrada")
                with col_i2:
                    cantidad_entrada = st.number_input("Cantidad que ingresa", min_value=1, value=1, step=1)
                with col_i3:
                    motivo_entrada = st.text_input("Motivo / N.º de factura", placeholder="Ej: Compra bodega OC-1023")
                registrar_entrada = st.form_submit_button("Registrar entrada", use_container_width=True)

            if registrar_entrada:
                idx = df_inventario[df_inventario["material"] == material_entrada].index[0]
                stock_actual = float(pd.to_numeric(df_inventario.loc[idx, "cantidad_actual"], errors="coerce") or 0)
                df_inventario.loc[idx, "cantidad_actual"] = stock_actual + cantidad_entrada
                guardar_inventario(df_inventario)

                nuevo_id_mov = siguiente_id(df_movimientos)
                fila_mov = {
                    "id": nuevo_id_mov,
                    "fecha": date.today().strftime("%Y-%m-%d"),
                    "tipo_movimiento": "Entrada",
                    "material": material_entrada,
                    "cantidad": cantidad_entrada,
                    "motivo": motivo_entrada.strip() or "Entrada de material",
                    "inspeccion_id": "",
                    "tecnico": "",
                }
                df_movimientos = pd.concat([df_movimientos, pd.DataFrame([fila_mov])], ignore_index=True)
                guardar_movimientos(df_movimientos)
                st.success(f"Entrada registrada: +{cantidad_entrada} de '{material_entrada}'.")
                st.rerun()

    st.markdown("##### 📋 Stock actual del taller")

    if df_inventario.empty:
        st.info("No hay materiales registrados todavía. Usa el formulario de arriba para agregar el primero.")
    else:
        df_inv_view = df_inventario.copy()
        df_inv_view["cantidad_actual"] = pd.to_numeric(df_inv_view["cantidad_actual"], errors="coerce").fillna(0)
        df_inv_view["cantidad_minima"] = pd.to_numeric(df_inv_view["cantidad_minima"], errors="coerce").fillna(0)
        df_inv_view["costo_unitario"] = pd.to_numeric(df_inv_view["costo_unitario"], errors="coerce").fillna(0)

        n_bajo_stock = int((df_inv_view["cantidad_actual"] <= df_inv_view["cantidad_minima"]).sum())
        if n_bajo_stock > 0:
            st.warning(f"⚠️ Hay **{n_bajo_stock}** material(es) en o por debajo del mínimo definido.")

        editado_inv = st.data_editor(
            df_inv_view,
            column_config={
                "id": st.column_config.NumberColumn("ID", disabled=True),
                "material": st.column_config.TextColumn("Material", disabled=True),
                "categoria": st.column_config.SelectboxColumn("Categoría", options=CATEGORIAS),
                "unidad": st.column_config.SelectboxColumn("Unidad", options=UNIDADES_MATERIAL),
                "cantidad_actual": st.column_config.NumberColumn("Cantidad actual", disabled=True),
                "cantidad_minima": st.column_config.NumberColumn("Cantidad mínima"),
                "costo_unitario": st.column_config.NumberColumn("Costo unitario ($ COP)", format="$ %.0f"),
                "ubicacion": st.column_config.TextColumn("Ubicación"),
                "notas": st.column_config.TextColumn("Notas"),
            },
            hide_index=True,
            use_container_width=True,
            key="editor_inventario",
        )

        col_g_inv1, col_g_inv2 = st.columns([1, 3])
        with col_g_inv1:
            if st.button("💾 Guardar cambios de inventario", use_container_width=True):
                guardar_inventario(editado_inv)
                st.success("Inventario actualizado.")
                st.rerun()
        with col_g_inv2:
            st.download_button(
                "⬇️ Descargar inventario (CSV)",
                data=df_inventario.to_csv(index=False).encode("utf-8"),
                file_name="inventario_taller.csv",
                mime="text/csv",
            )

        st.markdown("---")
        st.markdown("##### 📜 Historial de movimientos (entradas y salidas)")
        if df_movimientos.empty:
            st.info("Aún no hay movimientos registrados.")
        else:
            st.dataframe(
                df_movimientos.sort_values("id", ascending=False),
                hide_index=True,
                use_container_width=True,
            )


# ==============================================================================
# PÁGINA 3 · REPUESTOS POR COMPRAR
# ==============================================================================
elif pagina == "🔧 Repuestos por Comprar":
    st.markdown('<p class="titulo-app">🔧 Repuestos Menores para Dejar en Stock</p>', unsafe_allow_html=True)
    st.markdown(
        '<p class="subtitulo-app">Fusibles, relés y terminales que deben quedar listos para no detener '
        'la máquina cuando salga de standby.</p>',
        unsafe_allow_html=True,
    )
    st.markdown("---")

    with st.expander("➕ Agregar repuesto manualmente (sin pasar por una inspección)"):
        with st.form("form_stock_manual", clear_on_submit=True):
            c1, c2, c3, c4 = st.columns(4)
            with c1:
                repuesto_m = st.text_input("Repuesto", placeholder="Ej: Fusible 20A")
            with c2:
                cantidad_m = st.number_input("Cantidad", min_value=1, value=1, step=1)
            with c3:
                prioridad_m = st.selectbox("Prioridad", PRIORIDADES, key="prioridad_manual")
            with c4:
                origen_m = st.text_input("Máquina de origen", placeholder="Ej: Tractor Alce 05")
            notas_m = st.text_input("Notas (opcional)")
            enviar_manual = st.form_submit_button("Agregar a la lista de stock")

        if enviar_manual:
            if not repuesto_m.strip():
                st.error("Escribe el nombre del repuesto.")
            else:
                nuevo_id_stock = siguiente_id(df_stock)
                fila_manual = {
                    "id": nuevo_id_stock,
                    "fecha_solicitud": date.today().strftime("%Y-%m-%d"),
                    "repuesto": repuesto_m.strip(),
                    "cantidad": int(cantidad_m),
                    "prioridad": prioridad_m,
                    "origen_maquina": origen_m.strip() or "No especificado",
                    "componente_relacionado": "",
                    "estado_stock": "Pendiente por solicitar",
                    "notas": notas_m.strip(),
                }
                df_stock = pd.concat([df_stock, pd.DataFrame([fila_manual])], ignore_index=True)
                guardar_stock(df_stock)
                st.success(f"'{repuesto_m.strip()}' agregado a la lista de repuestos.")
                st.rerun()

    st.markdown("##### 📦 Lista de repuestos pendientes")

    if df_stock.empty:
        st.info("No hay repuestos registrados todavía.")
    else:
        df_stock_edit = df_stock.copy()
        df_stock_edit["cantidad"] = pd.to_numeric(df_stock_edit["cantidad"], errors="coerce").fillna(1).astype(int)

        editado = st.data_editor(
            df_stock_edit,
            column_config={
                "id": st.column_config.NumberColumn("ID", disabled=True),
                "fecha_solicitud": st.column_config.TextColumn("Fecha", disabled=True),
                "repuesto": st.column_config.TextColumn("Repuesto", disabled=True),
                "cantidad": st.column_config.NumberColumn("Cantidad", disabled=True),
                "prioridad": st.column_config.SelectboxColumn("Prioridad", options=PRIORIDADES),
                "origen_maquina": st.column_config.TextColumn("Origen", disabled=True),
                "componente_relacionado": st.column_config.TextColumn("Componente relacionado", disabled=True),
                "estado_stock": st.column_config.SelectboxColumn("Estado de gestión", options=ESTADOS_STOCK),
                "notas": st.column_config.TextColumn("Notas"),
            },
            hide_index=True,
            use_container_width=True,
            key="editor_stock",
        )

        col_guardar, col_export = st.columns([1, 3])
        with col_guardar:
            if st.button("💾 Guardar cambios de stock", use_container_width=True):
                guardar_stock(editado)
                st.success("Lista de repuestos actualizada.")
                st.rerun()
        with col_export:
            st.download_button(
                "⬇️ Descargar lista de repuestos (CSV)",
                data=df_stock.to_csv(index=False).encode("utf-8"),
                file_name="stock_repuestos_mepp.csv",
                mime="text/csv",
            )


# ==============================================================================
# PÁGINA 3.5 · PRESUPUESTO POR MÁQUINA
# ==============================================================================
elif pagina == "💰 Presupuesto por Máquina":
    st.markdown('<p class="titulo-app">💰 Presupuesto de Repuestos por Máquina</p>', unsafe_allow_html=True)
    st.markdown(
        '<p class="subtitulo-app">Asigna el presupuesto mensual que te informe el Ingenio para cada '
        'máquina, y IncaVolt calcula automáticamente cuánto llevas gastado según el material que '
        'descuentas del inventario en cada reparación.</p>',
        unsafe_allow_html=True,
    )
    st.caption(
        "ℹ️ Esta app no está conectada al sistema interno de Incauca — el presupuesto lo ingresas tú "
        "manualmente (lo que te informe tu jefatura o Sistemas). El gasto sí se calcula automático a "
        "partir del inventario que ya llevas en la app."
    )
    st.markdown("---")

    with st.expander("➕ Asignar o actualizar presupuesto de una máquina"):
        with st.form("form_presupuesto", clear_on_submit=True):
            c1, c2, c3, c4 = st.columns(4)
            with c1:
                id_maquina_presu = st.text_input("Identificador de máquina", placeholder="Ej: Cosechadora CH-08")
            with c2:
                tipo_maquina_presu = st.selectbox("Tipo de máquina", TIPOS_MAQUINA, key="tipo_maquina_presu")
            with c3:
                periodo_presu = st.text_input("Período (mes)", value=date.today().strftime("%Y-%m"), placeholder="YYYY-MM")
            with c4:
                monto_presu = st.number_input("Presupuesto asignado ($ COP)", min_value=0.0, value=0.0, step=10000.0)
            notas_presu = st.text_input("Notas (opcional)", placeholder="Ej: Aprobado por jefatura de mantenimiento")
            guardar_presu_btn = st.form_submit_button("Guardar presupuesto", use_container_width=True)

        if guardar_presu_btn:
            if not id_maquina_presu.strip() or not periodo_presu.strip():
                st.error("Completa al menos el identificador de la máquina y el período (YYYY-MM).")
            else:
                existe = df_presupuesto[
                    (df_presupuesto["identificador_maquina"] == id_maquina_presu.strip())
                    & (df_presupuesto["periodo"] == periodo_presu.strip())
                ]
                if not existe.empty:
                    idx = existe.index[0]
                    df_presupuesto.loc[idx, "presupuesto_asignado"] = float(monto_presu)
                    df_presupuesto.loc[idx, "tipo_maquina"] = tipo_maquina_presu
                    df_presupuesto.loc[idx, "notas"] = notas_presu.strip()
                    st.success(f"Presupuesto de {id_maquina_presu.strip()} ({periodo_presu.strip()}) actualizado.")
                else:
                    nuevo_id_presu = siguiente_id(df_presupuesto)
                    fila_presu = {
                        "id": nuevo_id_presu,
                        "identificador_maquina": id_maquina_presu.strip(),
                        "tipo_maquina": tipo_maquina_presu,
                        "periodo": periodo_presu.strip(),
                        "presupuesto_asignado": float(monto_presu),
                        "notas": notas_presu.strip(),
                    }
                    df_presupuesto = pd.concat([df_presupuesto, pd.DataFrame([fila_presu])], ignore_index=True)
                    st.success(f"Presupuesto asignado a {id_maquina_presu.strip()} para {periodo_presu.strip()}.")
                guardar_presupuesto(df_presupuesto)
                st.rerun()

    st.markdown("##### 📊 Presupuesto vs. gasto ejecutado")

    if df_presupuesto.empty:
        st.info("Aún no has asignado presupuesto a ninguna máquina. Usa el formulario de arriba para empezar.")
    else:
        # Calcular el gasto real: movimientos de Salida (material usado en reparaciones)
        # cruzados con la inspección (para saber de qué máquina fue) y el costo unitario del inventario.
        df_gasto = pd.DataFrame(columns=["identificador_maquina", "periodo", "gasto"])
        if not df_movimientos.empty and not df_insp.empty:
            mov_salidas = df_movimientos[df_movimientos["tipo_movimiento"] == "Salida"].copy()
            if not mov_salidas.empty:
                mov_salidas["cantidad"] = pd.to_numeric(mov_salidas["cantidad"], errors="coerce").fillna(0)
                mov_salidas["periodo"] = mov_salidas["fecha"].astype(str).str.slice(0, 7)

                mapa_maquina = df_insp.set_index(df_insp["id"].astype(str))["identificador"].to_dict()
                mov_salidas["identificador_maquina"] = mov_salidas["inspeccion_id"].astype(str).map(mapa_maquina)

                mapa_costo = df_inventario.set_index("material")["costo_unitario"].apply(
                    lambda x: pd.to_numeric(x, errors="coerce") or 0
                ).to_dict()
                mov_salidas["costo_unitario"] = mov_salidas["material"].map(mapa_costo).fillna(0)
                mov_salidas["gasto"] = mov_salidas["cantidad"] * mov_salidas["costo_unitario"]

                df_gasto = (
                    mov_salidas.dropna(subset=["identificador_maquina"])
                    .groupby(["identificador_maquina", "periodo"])["gasto"]
                    .sum()
                    .reset_index()
                )

        df_presu_view = df_presupuesto.copy()
        df_presu_view["presupuesto_asignado"] = pd.to_numeric(
            df_presu_view["presupuesto_asignado"], errors="coerce"
        ).fillna(0)
        df_presu_view = df_presu_view.merge(
            df_gasto, on=["identificador_maquina", "periodo"], how="left"
        )
        df_presu_view["gasto"] = df_presu_view["gasto"].fillna(0)
        df_presu_view["saldo"] = df_presu_view["presupuesto_asignado"] - df_presu_view["gasto"]
        df_presu_view["% usado"] = df_presu_view.apply(
            lambda r: round((r["gasto"] / r["presupuesto_asignado"]) * 100, 1) if r["presupuesto_asignado"] > 0 else 0,
            axis=1,
        )

        for _, fila in df_presu_view.sort_values(["periodo", "identificador_maquina"], ascending=[False, True]).iterrows():
            pct = fila["% usado"]
            if pct >= 100:
                color_barra = ESTADO_INFO["Rojo"]["color"]
            elif pct >= 75:
                color_barra = ESTADO_INFO["Amarillo"]["color"]
            else:
                color_barra = ESTADO_INFO["Verde"]["color"]

            with st.container(border=True):
                c1, c2, c3 = st.columns([2.2, 1.3, 1.5])
                with c1:
                    st.markdown(f"**{fila['identificador_maquina']}** · {fila['tipo_maquina']}")
                    st.caption(f"Período: {fila['periodo']}" + (f" · {fila['notas']}" if fila['notas'] else ""))
                with c2:
                    st.markdown(f"Presupuesto: **${fila['presupuesto_asignado']:,.0f}**")
                    st.markdown(f"Gastado: **${fila['gasto']:,.0f}**")
                with c3:
                    st.markdown(f"Saldo: **${fila['saldo']:,.0f}**")
                    st.markdown(
                        f'<span class="badge" style="background-color:{color_barra}; '
                        f'box-shadow:0 0 16px {color_barra};">{pct}% usado</span>',
                        unsafe_allow_html=True,
                    )
                st.progress(min(int(pct), 100))

        with st.expander("⬇️ Exportar presupuesto y gasto (CSV)"):
            st.download_button(
                "Descargar presupuesto_maquinas.csv",
                data=df_presu_view.to_csv(index=False).encode("utf-8"),
                file_name="presupuesto_maquinas.csv",
                mime="text/csv",
            )


# ==============================================================================
# PÁGINA 4 · DASHBOARD SUPERVISOR
# ==============================================================================
elif pagina == "📊 Dashboard Supervisor":
    st.markdown('<p class="titulo-app">📊 Panel de Supervisión de Mantenimiento Eléctrico</p>', unsafe_allow_html=True)
    st.markdown(
        '<p class="subtitulo-app">Visión general para que la jefatura organice compras y priorice '
        'intervenciones antes del arranque de zafra.</p>',
        unsafe_allow_html=True,
    )
    st.markdown("---")

    if df_insp.empty:
        st.info("Aún no hay datos suficientes. Registra inspecciones para ver el panel.")
    else:
        df_dash = df_insp.copy()

        col_ft1, col_ft2 = st.columns(2)
        with col_ft1:
            filtro_tipo_d = st.multiselect(
                "Filtrar por tipo de máquina", TIPOS_MAQUINA, default=TIPOS_MAQUINA, key="dash_tipo"
            )
        with col_ft2:
            filtro_cat_d = st.multiselect(
                "Filtrar por categoría", CATEGORIAS, default=CATEGORIAS, key="dash_cat"
            )

        df_dash = df_dash[
            df_dash["tipo_maquina"].isin(filtro_tipo_d) & df_dash["categoria"].isin(filtro_cat_d)
        ]

        total = len(df_dash)
        n_verde = int((df_dash["estado"] == "Verde").sum())
        n_amarillo = int((df_dash["estado"] == "Amarillo").sum())
        n_rojo = int((df_dash["estado"] == "Rojo").sum())
        pct_critico = round(((n_amarillo + n_rojo) / total) * 100, 1) if total else 0.0

        n_stock_pend = int((df_stock["estado_stock"] == "Pendiente por solicitar").sum()) if not df_stock.empty else 0
        n_stock_solicitado = int((df_stock["estado_stock"] == "Solicitado a bodega").sum()) if not df_stock.empty else 0

        k1, k2, k3, k4, k5 = st.columns(5)
        tarjetas = [
            (k1, "Componentes revisados", total, "#5CF2C2"),
            (k2, "🟢 Operativos", n_verde, ESTADO_INFO["Verde"]["color"]),
            (k3, "🟡 En alerta", n_amarillo, ESTADO_INFO["Amarillo"]["color"]),
            (k4, "🔴 Críticos", n_rojo, ESTADO_INFO["Rojo"]["color"]),
            (k5, "% en alerta / crítico", f"{pct_critico}%", "#8BD8FF"),
        ]
        for col, titulo, valor, color in tarjetas:
            with col:
                st.markdown(
                    f"""
                    <div class="card-kpi" style="border-color:{color}; box-shadow:0 0 22px {color}55, inset 0 0 20px rgba(255,255,255,0.03); color:{color};">
                        <h1>{valor}</h1>
                        <p style="color:#E8FFF3;">{titulo}</p>
                    </div>
                    """,
                    unsafe_allow_html=True,
                )

        st.markdown("<br>", unsafe_allow_html=True)

        col_g1, col_g2 = st.columns(2)

        with col_g1:
            st.markdown("##### Distribución de estados por categoría de componente")
            if total:
                resumen_cat = (
                    df_dash.groupby(["categoria", "estado"]).size().reset_index(name="cantidad")
                )
                fig_barras = px.bar(
                    resumen_cat,
                    x="categoria",
                    y="cantidad",
                    color="estado",
                    barmode="stack",
                    color_discrete_map={
                        "Verde": ESTADO_INFO["Verde"]["color"],
                        "Amarillo": ESTADO_INFO["Amarillo"]["color"],
                        "Rojo": ESTADO_INFO["Rojo"]["color"],
                    },
                    labels={"categoria": "Categoría", "cantidad": "Cantidad", "estado": "Estado"},
                )
                fig_barras.update_layout(legend_title_text="Estado", height=380)
                st.plotly_chart(fig_barras, use_container_width=True)
            else:
                st.info("Sin datos para graficar con los filtros actuales.")

        with col_g2:
            st.markdown("##### Proporción general de estados")
            if total:
                resumen_estado = df_dash["estado"].value_counts().reset_index()
                resumen_estado.columns = ["estado", "cantidad"]
                fig_dona = px.pie(
                    resumen_estado,
                    names="estado",
                    values="cantidad",
                    hole=0.55,
                    color="estado",
                    color_discrete_map={
                        "Verde": ESTADO_INFO["Verde"]["color"],
                        "Amarillo": ESTADO_INFO["Amarillo"]["color"],
                        "Rojo": ESTADO_INFO["Rojo"]["color"],
                    },
                )
                fig_dona.update_layout(height=380)
                st.plotly_chart(fig_dona, use_container_width=True)
            else:
                st.info("Sin datos para graficar con los filtros actuales.")

        st.markdown("---")

        col_h1, col_h2 = st.columns(2)
        with col_h1:
            st.markdown("##### 🔴 Máquinas con componentes críticos (requieren acción urgente)")
            criticos = df_dash[df_dash["estado"] == "Rojo"][
                ["identificador", "tipo_maquina", "componente", "fecha", "tecnico"]
            ].sort_values("fecha", ascending=False)
            if criticos.empty:
                st.success("No hay componentes en estado crítico. ✅")
            else:
                st.dataframe(criticos, hide_index=True, use_container_width=True)

        with col_h2:
            st.markdown("##### 🔧 Repuestos pendientes para gestionar compra")
            m1, m2 = st.columns(2)
            m1.metric("Pendientes por solicitar", n_stock_pend)
            m2.metric("Ya solicitados a bodega", n_stock_solicitado)
            if not df_stock.empty:
                pendientes_stock = df_stock[
                    df_stock["estado_stock"] != "Recibido / Listo en stock"
                ][["repuesto", "cantidad", "prioridad", "origen_maquina", "estado_stock"]]
                st.dataframe(pendientes_stock, hide_index=True, use_container_width=True)
            else:
                st.info("No hay repuestos registrados todavía.")
