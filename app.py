"""
==================================================================================
 APP: INCAVOLT - Mantenimiento Eléctrico Preventivo y Predictivo
 Ingenio Incauca
 Alcance: Cosechadoras John Deere Case y Tractores Game (equipos en Standby)
 Desarrollado por: [Cristian Andres Rubio] · Electricista de Cosechadoras y Tractores
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
            addTag('meta', {name: 'theme-color', content: '#1B4332'});
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

COLUMNAS_INSPECCION = [
    "id", "fecha", "hora", "tipo_maquina", "identificador", "categoria",
    "componente", "estado", "observaciones", "tecnico",
]

COLUMNAS_STOCK = [
    "id", "fecha_solicitud", "repuesto", "cantidad", "prioridad",
    "origen_maquina", "componente_relacionado", "estado_stock", "notas",
]

CATEGORIAS = ["Sensor", "Relé", "Fusible", "Cableado / Ramal", "Luces / Señalización", "Otro"]
TIPOS_MAQUINA = ["Cosechadora John Deere", "Tractor de Alce"]
ESTADOS = ["Verde", "Amarillo", "Rojo"]

ESTADO_INFO = {
    "Verde":    {"emoji": "🟢", "label": "Operativo",  "color": "#2E7D32", "desc": "Componente en condición normal, sin novedad."},
    "Amarillo": {"emoji": "🟡", "label": "Alerta",     "color": "#F2A900", "desc": "Puede continuar operando bajo monitoreo preventivo."},
    "Rojo":     {"emoji": "🔴", "label": "Crítico",    "color": "#C62828", "desc": "Requiere cambio o intervención urgente."},
}

PRIORIDADES = ["Alta", "Media", "Baja"]
ESTADOS_STOCK = ["Pendiente por solicitar", "Solicitado a bodega", "Recibido / Listo en stock"]


# ----------------------------------------------------------------------------
# CAPA DE DATOS (CSV como persistencia simple para el prototipo)
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
    .badge {
        display: inline-block;
        padding: 3px 12px;
        border-radius: 14px;
        color: white;
        font-weight: 600;
        font-size: 0.85rem;
        text-align: center;
    }
    .card-kpi {
        border-radius: 10px;
        padding: 18px 16px;
        color: white;
        text-align: center;
    }
    .card-kpi h1 { margin: 0; font-size: 2.1rem; }
    .card-kpi p { margin: 0; font-size: 0.9rem; opacity: 0.92; }
    .titulo-app {
        font-size: 1.9rem;
        font-weight: 800;
        color: #1B4332;
        margin-bottom: 0px;
    }
    .subtitulo-app {
        color: #555;
        margin-top: 0px;
        font-size: 0.95rem;
    }
    </style>
    """,
    unsafe_allow_html=True,
)


def badge_estado(estado: str) -> str:
    info = ESTADO_INFO.get(estado, {"color": "#999", "emoji": "⚪", "label": estado})
    return f'<span class="badge" style="background-color:{info["color"]};">{info["emoji"]} {info["label"]}</span>'


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
            "🚦 Historial de Estados",
            "🔧 Stock de Repuestos",
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
elif pagina == "🚦 Historial de Estados":
    st.markdown('<p class="titulo-app">🚦 Historial y Semáforo de Estados</p>', unsafe_allow_html=True)
    st.markdown(
        '<p class="subtitulo-app">Consulta todas las inspecciones registradas y actualiza el estado '
        'cuando cambie la condición del componente.</p>',
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

        with st.expander("⬇️ Exportar historial completo (CSV)"):
            st.download_button(
                "Descargar inspecciones.csv",
                data=df_insp.to_csv(index=False).encode("utf-8"),
                file_name="inspecciones_mepp.csv",
                mime="text/csv",
            )


# ==============================================================================
# PÁGINA 3 · STOCK DE REPUESTOS
# ==============================================================================
elif pagina == "🔧 Stock de Repuestos":
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
            (k1, "Componentes revisados", total, "#2C3E50"),
            (k2, "🟢 Operativos", n_verde, ESTADO_INFO["Verde"]["color"]),
            (k3, "🟡 En alerta", n_amarillo, ESTADO_INFO["Amarillo"]["color"]),
            (k4, "🔴 Críticos", n_rojo, ESTADO_INFO["Rojo"]["color"]),
            (k5, "% en alerta / crítico", f"{pct_critico}%", "#6D4C41"),
        ]
        for col, titulo, valor, color in tarjetas:
            with col:
                st.markdown(
                    f"""
                    <div class="card-kpi" style="background-color:{color};">
                        <h1>{valor}</h1>
                        <p>{titulo}</p>
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
