# MEPP Digital — Mantenimiento Eléctrico Preventivo

Prototipo Streamlit para la gestión de inspecciones eléctricas preventivas en
cosechadoras John Deere y tractores de alce en standby, dentro del Ingenio.

## 1. Requisitos
- Python 3.9 o superior instalado.

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

## 5. Módulos de la aplicación

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
