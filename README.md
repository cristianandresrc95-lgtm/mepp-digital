# IncaVolt — Mantenimiento Eléctrico Preventivo (Ingenio Incauca)

Prototipo Streamlit para la gestión de inspecciones eléctricas preventivas en
cosechadoras John Deere y tractores de alce en standby, dentro del Ingenio Incauca.

> Antes de compartirla, abre `app.py` y reemplaza `[Tu Nombre]` (aparece en la
> variable `DESARROLLADOR`, cerca de la línea 15) por tu nombre real — así
> queda tu crédito visible en la barra lateral de la app.

## 0. Estructura de archivos (importante para subir a GitHub)

```
mepp-digital/
├── app.py
├── requirements.txt
├── README.md
├── .streamlit/
│   └── config.toml          ← colores de marca + habilita archivos estáticos
└── static/
    ├── manifest.json         ← hace que la app se vea como app nativa
    ├── icon-192.png
    ├── icon-512.png
    └── apple-touch-icon.png
```

**Importante:** las carpetas `.streamlit/` y `static/` deben subirse completas
a GitHub, respetando sus nombres exactos (incluido el punto inicial de
`.streamlit`). Si tu explorador de archivos oculta `.streamlit` por ser una
carpeta con punto, en la subida de GitHub arrástrala igual — GitHub sí la
reconoce sin problema.

## 1. Requisitos
- Python 3.9 o superior instalado (solo si quieres correrla en tu PC; para
  celular no se necesita instalar nada, ver sección 6).

## 2. Instalación (una sola vez)

Abre una terminal en esta carpeta y ejecuta:

```bash
pip install -r requirements.txt
```

## 3. Ejecutar la aplicación

```bash
streamlit run app.py
```

Se abrirá automáticamente en el navegador (normalmente en `http://localhost:8501`).
Puedes compartir esa misma URL con otros equipos conectados a la red interna
del Ingenio cambiando el host de arranque:

```bash
streamlit run app.py --server.address 0.0.0.0 --server.port 8501
```

y accediendo desde otro PC con `http://IP-DE-TU-EQUIPO:8501`.

## 4. Persistencia de datos

El prototipo guarda la información en dos archivos CSV que se crean
automáticamente junto a `app.py`:

- `inspecciones.csv` → historial de inspecciones eléctricas.
- `stock_repuestos.csv` → repuestos menores pendientes de gestionar.

Esto permite que los datos no se pierdan al cerrar el navegador o reiniciar
la app. Para un despliegue definitivo en el Ingenio, se recomienda migrar
esta capa a una base de datos (SQLite o PostgreSQL) sin modificar el resto
del código, ya que toda la lectura/escritura está aislada en las funciones
`cargar_inspecciones()`, `guardar_inspecciones()`, `cargar_stock()` y
`guardar_stock()`.

## 6. Instalarla en el celular como si fuera una app

No requiere Play Store ni App Store. Una vez desplegada en Streamlit Cloud:

**Android (Chrome):**
1. Abre la URL de la app (ej. `incavolt.streamlit.app`)
2. Toca los 3 puntitos (⋮) arriba a la derecha
3. Toca "Añadir a pantalla de inicio"
4. Con el manifest y los íconos ya incluidos, se abrirá a pantalla completa,
   sin barra de navegador, con el ícono de rayo verde/amarillo de IncaVolt.

**iPhone (Safari):**
1. Abre la URL de la app
2. Toca el ícono de compartir (cuadro con flecha hacia arriba)
3. Toca "Añadir a pantalla de inicio"

## 7. Módulos de la aplicación

1. **📋 Registrar Inspección** — formulario para registrar el componente
   eléctrico revisado (sensor, relé, fusible, cableado, luces), su estado
   (semáforo Verde/Amarillo/Rojo) y, si aplica, el repuesto que debe quedar
   listo en stock.
2. **🚦 Historial de Estados** — lista filtrable de todas las inspecciones
   con su semáforo visual, y opción para actualizar el estado de un
   componente ya registrado (por ejemplo, si pasó de Amarillo a Rojo).
3. **🔧 Stock de Repuestos** — lista editable de fusibles, relés y
   terminales pendientes por solicitar, solicitados o ya recibidos.
4. **📊 Dashboard Supervisor** — métricas y gráficos para que la jefatura
   vea de un vistazo cuántos componentes están en alerta o críticos, por
   categoría y por máquina, y qué repuestos debe gestionar.
