import pandas as pd
import streamlit as st

from prismastock import (
    calcular_existencias_finales,
    clasificar_estado,
    consumo_promedio,
    datos_demo,
    dias_hasta_agotarse,
    dias_hasta_minimo,
    inventario_en_el_tiempo,
    sumar_filas,
)

CODE = "Código"
INITIAL_STOCK = "Stock inicial"
MINIMUM_STOCK = "Stock mínimo"
OPTIMAL_STOCK = "Stock óptimo"
DEMO_MODE = "Demostración"


st.set_page_config(
    page_title="PrismaStock | Inventario",
    page_icon="📦",
    layout="wide",
    initial_sidebar_state="expanded",
)

st.markdown(
    """
    <style>
    :root {
        --ink: #172a26;
        --muted: #60736d;
        --green: #176b55;
        --lime: #d7ed7a;
        --paper: #f5f7f1;
        --line: #dce5dc;
    }
    .stApp { background: var(--paper); color: var(--ink); }
    [data-testid="stSidebar"] { background: #e9efe5; }
    [data-testid="stSidebar"] h2 { color: var(--green); }
    .block-container { padding-top: 2rem; max-width: 1440px; }
    .brand { border-bottom: 1px solid var(--line); padding-bottom: 1.1rem; margin-bottom: 1.3rem; }
    .brand-kicker { color: var(--green); font-size: .78rem; font-weight: 700; text-transform: uppercase; letter-spacing: .12em; }
    .brand h1 { margin: .2rem 0 0; color: var(--ink); font-size: 2.25rem; }
    .brand p { color: var(--muted); margin: .35rem 0 0; }
    div[data-testid="stMetric"] { background: white; border: 1px solid var(--line); padding: 1rem; border-radius: 6px; }
    div[data-testid="stMetricLabel"] { color: var(--muted); }
    div[data-testid="stMetricValue"] { color: var(--green); }
    div.stButton > button[kind="primary"] { background: var(--green); border-color: var(--green); }
    </style>
    """,
    unsafe_allow_html=True,
)


def build_demo_products():
    codes, names, initial, minimum, optimal, _, _, _ = datos_demo()
    return pd.DataFrame(
        {
            CODE: codes,
            "Producto": names,
            INITIAL_STOCK: initial,
            MINIMUM_STOCK: minimum,
            OPTIMAL_STOCK: optimal,
        }
    )


def movement_frame(products, days, values=None):
    data = {f"Día {day + 1}": [0] * len(products) for day in range(days)}
    if values is not None:
        for product_index in range(len(products)):
            for day in range(days):
                data[f"Día {day + 1}"][product_index] = values[product_index][day]
    frame = pd.DataFrame(data)
    frame.insert(0, "Producto", products)
    return frame


def compute_results(products, sales, restocks, days, horizon):
    initial = products[INITIAL_STOCK].astype(int).tolist()
    minimum = products[MINIMUM_STOCK].astype(int).tolist()
    optimal = products[OPTIMAL_STOCK].astype(int).tolist()
    codes = products[CODE].astype(str).tolist()
    names = products["Producto"].astype(str).tolist()
    sales_matrix = sales.drop(columns="Producto").astype(int).values.tolist()
    restock_matrix = restocks.drop(columns="Producto").astype(int).values.tolist()

    sold = sumar_filas(sales_matrix)
    received = sumar_filas(restock_matrix)
    final = calcular_existencias_finales(initial, sold, received)
    results = []

    for index, name in enumerate(names):
        average = consumo_promedio(sold[index], days)
        days_to_minimum = dias_hasta_minimo(final[index], average, minimum[index])
        status = clasificar_estado(final[index], minimum[index], days_to_minimum)
        results.append(
            {
                CODE: codes[index],
                "Producto": name,
                "Inicial": initial[index],
                "Ventas": sold[index],
                "Reposiciones": received[index],
                "Stock actual": final[index],
                "Mínimo": minimum[index],
                "Consumo/día": average,
                "Días al mínimo": days_to_minimum,
                "Estado": status,
                "Comprar": max(optimal[index] - final[index], 0),
                "Días al agotamiento": dias_hasta_agotarse(final[index], average),
            }
        )

    projection = pd.DataFrame(
        {
            name: [
                max(inventario_en_el_tiempo(final[index], results[index]["Consumo/día"], day), 0)
                for day in range(horizon + 1)
            ]
            for index, name in enumerate(names)
        },
        index=[f"Día {day}" for day in range(horizon + 1)],
    )
    return pd.DataFrame(results), projection, sum(sold), sum(final)


st.markdown(
    """
    <div class="brand">
      <div class="brand-kicker">Control inteligente de inventario</div>
      <h1>PrismaStock</h1>
      <p>Existencias, movimiento del período y señales de reposición en un solo lugar.</p>
    </div>
    """,
    unsafe_allow_html=True,
)

with st.sidebar:
    st.header("Configuración")
    mode = st.radio("Datos", [DEMO_MODE, "Mi inventario"], horizontal=False)
    period_days = st.number_input("Días del período", min_value=1, max_value=365, value=5 if mode == DEMO_MODE else 7)
    horizon = st.slider("Días a proyectar", min_value=1, max_value=30, value=7)
    st.caption("Las alertas comparan el stock proyectado con el mínimo de seguridad.")

is_demo = mode == DEMO_MODE
if is_demo:
    default_products = build_demo_products()
else:
    default_products = pd.DataFrame(
        [{CODE: "P01", "Producto": "Producto nuevo", INITIAL_STOCK: 0, MINIMUM_STOCK: 0, OPTIMAL_STOCK: 1}]
    )

products = st.data_editor(
    default_products,
    key="products_demo" if is_demo else "products_custom",
    num_rows="dynamic",
    hide_index=True,
    width="stretch",
    column_config={
        CODE: st.column_config.TextColumn(CODE, required=True),
        "Producto": st.column_config.TextColumn("Producto", required=True),
        INITIAL_STOCK: st.column_config.NumberColumn(min_value=0, step=1, required=True),
        MINIMUM_STOCK: st.column_config.NumberColumn(min_value=0, step=1, required=True),
        OPTIMAL_STOCK: st.column_config.NumberColumn(min_value=1, step=1, required=True),
    },
)

tab_summary, tab_movements, tab_projection = st.tabs(["Resumen", "Movimientos", "Proyección"])

valid_products = not products.empty
if valid_products:
    products = products.dropna(subset=[CODE, "Producto"]).copy()
    products[CODE] = products[CODE].astype(str).str.strip().str.upper()
    products["Producto"] = products["Producto"].astype(str).str.strip()
    valid_products = (
        not products.empty
        and (products[CODE] != "").all()
        and (products["Producto"] != "").all()
        and products[CODE].is_unique
        and (products[OPTIMAL_STOCK] > products[MINIMUM_STOCK]).all()
    )

if not valid_products:
    st.warning("Completa el catálogo: cada producto necesita código y nombre únicos, y el stock óptimo debe superar el mínimo.")
else:
    product_names = products["Producto"].tolist()
    day_count = int(period_days)
    demo_data = datos_demo() if is_demo else None
    initial_sales = demo_data[5] if is_demo and day_count == 5 and len(products) == 3 else None
    initial_restocks = demo_data[6] if initial_sales is not None else None
    signature = f"{mode}_{len(products)}_{day_count}"
    sales_key = f"sales_{signature}"
    restocks_key = f"restocks_{signature}"
    if sales_key not in st.session_state:
        st.session_state[sales_key] = movement_frame(product_names, day_count, initial_sales)
        st.session_state[restocks_key] = movement_frame(product_names, day_count, initial_restocks)

    with tab_movements:
        st.subheader("Movimientos del período")
        st.caption("Ingresa unidades enteras por producto y día. En la demostración se cargan los datos del ejemplo.")
        left, right = st.columns(2)
        with left:
            st.markdown("**Ventas**")
            sales = st.data_editor(
                st.session_state[sales_key],
                key=f"sales_editor_{signature}",
                hide_index=True,
                width="stretch",
                column_config={
                    "Producto": st.column_config.TextColumn(disabled=True),
                    **{f"Día {day + 1}": st.column_config.NumberColumn(min_value=0, step=1) for day in range(day_count)},
                },
            )
        with right:
            st.markdown("**Reposiciones recibidas**")
            restocks = st.data_editor(
                st.session_state[restocks_key],
                key=f"restocks_editor_{signature}",
                hide_index=True,
                width="stretch",
                column_config={
                    "Producto": st.column_config.TextColumn(disabled=True),
                    **{f"Día {day + 1}": st.column_config.NumberColumn(min_value=0, step=1) for day in range(day_count)},
                },
            )

    values_valid = True
    for movement_data in (sales, restocks):
        numeric_values = movement_data.drop(columns="Producto").fillna(0)
        values_valid = values_valid and (numeric_values >= 0).all().all() and (numeric_values % 1 == 0).all().all()

    if values_valid:
        summary, projection, total_sold, total_stock = compute_results(
            products, sales, restocks, day_count, horizon
        )
        with tab_summary:
            metric_a, metric_b, metric_c = st.columns(3)
            metric_a.metric("Unidades vendidas", f"{total_sold:,}")
            metric_b.metric("Existencias actuales", f"{total_stock:,}")
            metric_c.metric("Productos con alerta", int((summary["Estado"] != "Normal").sum()))

            st.subheader("Estado por producto")
            st.dataframe(
                summary[[CODE, "Producto", "Inicial", "Ventas", "Reposiciones", "Stock actual", "Mínimo", "Estado"]],
                hide_index=True,
                width="stretch",
                column_config={"Estado": st.column_config.TextColumn("Estado")},
            )

            alerts = summary[summary["Estado"] != "Normal"]
            if alerts.empty:
                st.success("Todo en orden: ningún producto requiere reposición por ahora.")
            else:
                st.subheader("Atención de reposición")
                for _, item in alerts.iterrows():
                    message = (
                        f"**{item[CODE]} · {item['Producto']}**: {item['Stock actual']} unidades "
                        f"(mínimo {item['Mínimo']}). Compra **{item['Comprar']} unidades** para volver al stock óptimo."
                    )
                    if item["Estado"] == "ALERTA CRÍTICA":
                        st.error(message)
                    else:
                        st.warning(message)
                    if pd.notna(item["Días al agotamiento"]):
                        st.caption(f"Agotamiento estimado: {item['Días al agotamiento']:.1f} días.")

            csv = summary.to_csv(index=False).encode("utf-8-sig")
            st.download_button("Descargar resumen CSV", csv, "prismastock_resumen.csv", "text/csv")

        with tab_projection:
            st.subheader("Stock proyectado")
            st.caption("Estimación basada en el consumo diario promedio del período seleccionado.")
            st.line_chart(projection, height=360)
            st.dataframe(projection, width="stretch")
    else:
        st.warning("Los movimientos deben ser cantidades enteras iguales o mayores que cero.")