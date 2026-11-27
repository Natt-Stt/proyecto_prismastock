import pandas as pd
import streamlit as st

from prismastock import (
    analizar_periodo,
    datos_demo,
    inventario_en_el_tiempo,
)

CODE = "Codigo"
INITIAL_STOCK = "Stock inicial"
MINIMUM_STOCK = "Stock minimo"
OPTIMAL_STOCK = "Stock optimo"
DEMO_MODE = "Demostracion"

st.set_page_config(
    page_title="PrismaStock | Inventario",
    page_icon="📦",
    layout="wide",
)

st.markdown(
    """
    <style>
    :root {
        color-scheme: dark;
        --page: #101816;
        --sidebar: #182622;
        --surface: #1e2d28;
        --border: #354940;
        --text: #f1f5f2;
        --muted: #b7c7bf;
        --accent: #82ddb0;
    }
    .stApp { background: var(--page); color: var(--text); }
    [data-testid="stSidebar"] { background: var(--sidebar); }
    [data-testid="stHeader"] { background: rgba(16, 24, 22, 0.9); }
    .brand { border-bottom: 1px solid var(--border); padding-bottom: 1rem; margin-bottom: 1rem; }
    .brand h1, h1, h2, h3, h4 { color: var(--accent); }
    .brand h1 { margin-bottom: 0.2rem; }
    .brand p, .stCaption, [data-testid="stCaptionContainer"] { color: var(--muted); }
    .stMarkdown, .stText, label, [data-testid="stWidgetLabel"] { color: var(--text); }
    div[data-testid="stMetric"] {
        background: var(--surface);
        border: 1px solid var(--border);
        padding: 1rem;
        border-radius: 0.5rem;
    }
    div[data-testid="stMetricLabel"], div[data-testid="stMetricDelta"] { color: var(--muted); }
    div[data-testid="stMetricValue"] { color: var(--accent); }
    [data-baseweb="input"], [data-baseweb="select"], [data-baseweb="textarea"] {
        background: var(--surface);
        border-color: var(--border);
    }
    [data-baseweb="input"] input, [data-baseweb="textarea"] textarea {
        color: var(--text);
        -webkit-text-fill-color: var(--text);
    }
    div[data-testid="stDataFrame"], div[data-testid="stDataEditor"] {
        border: 1px solid var(--border);
        border-radius: 0.5rem;
    }
    div.stButton > button[kind="primary"], div.stDownloadButton > button {
        background: #246b50;
        border-color: #3a956c;
        color: #ffffff;
    }
    </style>
    """,
    unsafe_allow_html=True,
)


def demo_products():
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


def movement_frame(product_names, days, values=None):
    data = {f"Dia {day + 1}": [0] * len(product_names) for day in range(days)}
    if values is not None:
        for product_index in range(len(product_names)):
            for day in range(days):
                data[f"Dia {day + 1}"][product_index] = values[product_index][day]
    frame = pd.DataFrame(data)
    frame.insert(0, "Producto", product_names)
    return frame


def compute_results(products, sales, restocks, days, horizon):
    initial = products[INITIAL_STOCK].astype(int).tolist()
    minimum = products[MINIMUM_STOCK].astype(int).tolist()
    optimal = products[OPTIMAL_STOCK].astype(int).tolist()
    codes = products[CODE].astype(str).tolist()
    names = products["Producto"].astype(str).tolist()
    sales_matrix = sales.drop(columns="Producto").astype(int).values.tolist()
    restock_matrix = restocks.drop(columns="Producto").astype(int).values.tolist()

    results = analizar_periodo(initial, minimum, optimal,
                               sales_matrix, restock_matrix, days)
    rows = []
    for index, r in enumerate(results):
        rows.append(
            {
                CODE: codes[index],
                "Producto": names[index],
                "Inicial": r["inicial"],
                "Ventas": r["vendidas"],
                "Reposiciones": r["recibidas"],
                "Stock actual": r["final"],
                "Minimo": minimum[index],
                "Consumo/dia": r["consumo"],
                "Dias al minimo": r["dias_minimo"],
                "Estado": r["estado"],
                "Comprar": r["comprar"],
                "Dias al agotamiento": r["dias_agotamiento"],
            }
        )

    projection = pd.DataFrame(
        {
            names[i]: [
                max(inventario_en_el_tiempo(r["final"], r["consumo"], day), 0)
                for day in range(horizon + 1)
            ]
            for i, r in enumerate(results)
        },
        index=[f"Dia {day}" for day in range(horizon + 1)],
    )
    return (
        pd.DataFrame(rows),
        projection,
        sum(r["vendidas"] for r in results),
        sum(r["final"] for r in results),
    )


st.markdown(
    """
    <div class="brand">
      <h1>PrismaStock</h1>
      <p>Control y proyeccion de inventario para pequenos negocios.</p>
    </div>
    """,
    unsafe_allow_html=True,
)

with st.sidebar:
    st.header("Configuracion")
    mode = st.radio("Datos", [DEMO_MODE, "Mi inventario"])
    period_days = st.number_input(
        "Dias del periodo",
        min_value=1,
        max_value=365,
        value=5 if mode == DEMO_MODE else 7,
    )
    horizon = st.slider("Dias a proyectar", 1, 30, 7)

is_demo = mode == DEMO_MODE
if is_demo:
    default_products = demo_products()
else:
    default_products = pd.DataFrame(
        [
            {
                CODE: "P01",
                "Producto": "Producto nuevo",
                INITIAL_STOCK: 0,
                MINIMUM_STOCK: 0,
                OPTIMAL_STOCK: 1,
            }
        ]
    )

products = st.data_editor(
    default_products,
    key="products_demo" if is_demo else "products_custom",
    num_rows="dynamic",
    hide_index=True,
    column_config={
        CODE: st.column_config.TextColumn(required=True),
        "Producto": st.column_config.TextColumn(required=True),
        INITIAL_STOCK: st.column_config.NumberColumn(min_value=0, step=1, required=True),
        MINIMUM_STOCK: st.column_config.NumberColumn(min_value=0, step=1, required=True),
        OPTIMAL_STOCK: st.column_config.NumberColumn(min_value=1, step=1, required=True),
    },
)

tab_summary, tab_movements, tab_projection = st.tabs(
    ["Resumen", "Movimientos", "Proyeccion"]
)

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
    st.warning(
        "Complete el catalogo: codigos y nombres unicos, "
        "y stock optimo mayor que el minimo."
    )
else:
    product_names = products["Producto"].tolist()
    day_count = int(period_days)
    demo_data = datos_demo() if is_demo else None
    initial_sales = (
        demo_data[5]
        if is_demo and day_count == 5 and len(products) == 3
        else None
    )
    initial_restocks = demo_data[6] if initial_sales is not None else None

    signature = (
        f"{mode}_{len(products)}_{day_count}_"
        + "_".join(products[CODE].astype(str))
    )
    sales_key = f"sales_{signature}"
    restocks_key = f"restocks_{signature}"
    if sales_key not in st.session_state:
        st.session_state[sales_key] = movement_frame(
            product_names, day_count, initial_sales
        )
        st.session_state[restocks_key] = movement_frame(
            product_names, day_count, initial_restocks
        )

    st.session_state[sales_key]["Producto"] = product_names
    st.session_state[restocks_key]["Producto"] = product_names

    with tab_movements:
        st.subheader("Movimientos del periodo")
        left, right = st.columns(2)
        with left:
            st.markdown("**Ventas**")
            sales = st.data_editor(
                st.session_state[sales_key],
                key=f"sales_editor_{signature}",
                hide_index=True,
                column_config={
                    "Producto": st.column_config.TextColumn(disabled=True),
                    **{
                        f"Dia {day + 1}": st.column_config.NumberColumn(
                            min_value=0, step=1
                        )
                        for day in range(day_count)
                    },
                },
            )
        with right:
            st.markdown("**Reposiciones recibidas**")
            restocks = st.data_editor(
                st.session_state[restocks_key],
                key=f"restocks_editor_{signature}",
                hide_index=True,
                column_config={
                    "Producto": st.column_config.TextColumn(disabled=True),
                    **{
                        f"Dia {day + 1}": st.column_config.NumberColumn(
                            min_value=0, step=1
                        )
                        for day in range(day_count)
                    },
                },
            )

    numeric_valid = True
    for movements in (sales, restocks):
        values = movements.drop(columns="Producto").fillna(0)
        numeric_valid = (
            numeric_valid
            and (values >= 0).all().all()
            and (values % 1 == 0).all().all()
        )

    if numeric_valid:
        summary, projection, total_sold, total_stock = compute_results(
            products, sales, restocks, day_count, horizon
        )
        with tab_summary:
            metric_a, metric_b, metric_c = st.columns(3)
            metric_a.metric("Unidades vendidas", f"{total_sold:,}")
            metric_b.metric("Existencias finales", f"{total_stock:,}")
            metric_c.metric(
                "Productos con alerta",
                int((summary["Estado"] != "Normal").sum()),
            )

            st.subheader("Estado por producto")
            st.dataframe(
                summary[
                    [
                        CODE,
                        "Producto",
                        "Inicial",
                        "Ventas",
                        "Reposiciones",
                        "Stock actual",
                        "Minimo",
                        "Estado",
                    ]
                ],
                hide_index=True,
                use_container_width=True,
            )

            alerts = summary[summary["Estado"] != "Normal"]
            if alerts.empty:
                st.success("Ningun producto requiere reposicion por ahora.")
            else:
                st.subheader("Atencion de reposicion")
                for _, item in alerts.iterrows():
                    message = (
                        f"{item[CODE]} - {item['Producto']}: "
                        f"{item['Stock actual']} unidades "
                        f"(minimo {item['Minimo']}). "
                        f"Comprar {item['Comprar']} unidades."
                    )
                    if item["Estado"] == "ALERTA CRITICA":
                        st.error(message)
                    else:
                        st.warning(message)

            st.download_button(
                "Descargar resumen CSV",
                summary.to_csv(index=False).encode("utf-8-sig"),
                "prismastock_resumen.csv",
                "text/csv",
            )

        with tab_projection:
            st.subheader("Stock proyectado")
            st.line_chart(projection, height=360)
            st.dataframe(projection, use_container_width=True)
    else:
        st.warning("Los movimientos deben ser enteros iguales o mayores que cero.")
