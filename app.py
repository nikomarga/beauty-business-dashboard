import streamlit as st
import pandas as pd
import plotly.express as px

from analisis import (
    cargar_excel,
    calcular_resumen,
    ingresos_por_mes,
    analizar_servicios,
    analizar_clientes,
    analizar_pagos,
    comparar_meses,
    generar_conclusiones
)

from pdf import generar_pdf


st.set_page_config(
    page_title="Beauty Business Dashboard",
    page_icon="✨",
    layout="wide"
)

st.title("✨ Beauty Business Dashboard")

st.write(
    "Analiza tus ventas y conoce mejor el rendimiento de tu negocio."
)


archivo = st.file_uploader(
    "📁 Sube tu archivo Excel",
    type=["xlsx", "xlsm"]
)


if archivo is not None:

    try:

        df = cargar_excel(archivo)

        st.success(
            f"Archivo cargado correctamente. "
            f"Se encontraron {len(df)} ventas."
        )

        # =========================================================
        # PERIODO
        # =========================================================

        st.divider()

        st.subheader("📅 Periodo del informe")

        meses_disponibles = sorted(
            df["Fecha"].dt.to_period("M").unique()
        )

        opciones_periodo = ["Todo el periodo"] + [
            str(mes)
            for mes in meses_disponibles
        ]

        periodo_seleccionado = st.selectbox(
            "Selecciona el periodo que quieres analizar",
            opciones_periodo
        )

        # Filtrar información según el periodo seleccionado

        if periodo_seleccionado == "Todo el periodo":

            df_periodo = df.copy()

        else:

            periodo = pd.Period(
                periodo_seleccionado,
                freq="M"
            )

            df_periodo = df[
                df["Fecha"].dt.to_period("M") == periodo
            ].copy()


        # =========================================================
        # RESUMEN
        # =========================================================

        resumen = calcular_resumen(df_periodo)

        st.divider()

        st.subheader("📊 Resumen del negocio")

        col1, col2, col3 = st.columns(3)

        col1.metric(
            "💰 Facturación",
            f"{resumen['facturacion']:.2f} €"
        )

        col2.metric(
            "✨ Servicios",
            resumen["servicios"]
        )

        col3.metric(
            "👩 Clientes",
            resumen["clientes"]
        )


        col4, col5, col6 = st.columns(3)

        col4.metric(
            "🎟️ Ticket medio",
            f"{resumen['ticket_medio']:.2f} €"
        )

        col5.metric(
            "⏱️ Horas trabajadas",
            f"{resumen['horas']:.2f} h"
        )

        col6.metric(
            "💶 Ingreso por hora",
            f"{resumen['ingreso_hora']:.2f} €/h"
        )


        # =========================================================
        # EVOLUCIÓN HISTÓRICA
        # =========================================================

        st.divider()

        st.subheader("📈 Evolución de ingresos")

        mensual = ingresos_por_mes(df)

        grafico = px.bar(
            mensual,
            x="Mes",
            y="Ingresos",
            title="Facturación mensual"
        )

        st.plotly_chart(
            grafico,
            use_container_width=True
        )


        # =========================================================
        # COMPARACIÓN MENSUAL
        # =========================================================

        st.divider()

        st.subheader("📊 Comparación mensual")

        comparacion = None

        if len(meses_disponibles) >= 2:

            col1, col2 = st.columns(2)

            with col1:

                mes_actual = st.selectbox(
                    "Mes actual",
                    meses_disponibles,
                    index=len(meses_disponibles) - 1
                )

            with col2:

                meses_anteriores = [
                    mes
                    for mes in meses_disponibles
                    if mes != mes_actual
                ]

                mes_anterior = st.selectbox(
                    "Comparar con",
                    meses_anteriores,
                    index=len(meses_anteriores) - 1
                )


            comparacion = comparar_meses(
                df,
                mes_actual,
                mes_anterior
            )


            for _, fila in comparacion.iterrows():

                indicador = fila["Indicador"]

                anterior = fila["Mes anterior"]
                actual = fila["Mes actual"]
                cambio = fila["Cambio %"]


                if indicador in [
                    "Facturación",
                    "Ticket medio",
                    "€/hora"
                ]:

                    anterior_texto = f"{anterior:.2f} €"
                    actual_texto = f"{actual:.2f} €"

                else:

                    anterior_texto = f"{anterior:.2f}"
                    actual_texto = f"{actual:.2f}"


                if cambio > 0:

                    cambio_texto = f"↑ {cambio:.1f}%"

                elif cambio < 0:

                    cambio_texto = f"↓ {abs(cambio):.1f}%"

                else:

                    cambio_texto = "→ 0%"


                col1, col2, col3 = st.columns(3)

                col1.metric(
                    indicador,
                    actual_texto,
                    cambio_texto
                )

                col2.write(
                    f"Mes anterior: **{anterior_texto}**"
                )

                col3.write(
                    f"Mes actual: **{actual_texto}**"
                )

                st.divider()

        else:

            st.info(
                "Necesitas al menos dos meses de datos "
                "para realizar una comparación."
            )


        # =========================================================
        # SERVICIOS
        # =========================================================

        st.divider()

        st.subheader("✨ Rendimiento de servicios")

        servicios = analizar_servicios(df_periodo)

        st.dataframe(
            servicios,
            use_container_width=True,
            hide_index=True
        )


        # =========================================================
        # CLIENTES
        # =========================================================

        st.divider()

        st.subheader("👩 Clientes")

        clientes = analizar_clientes(df_periodo)

        st.divider()

        st.subheader("💡 Conclusiones automáticas")

        mensual_periodo = ingresos_por_mes(df_periodo)

        conclusiones = generar_conclusiones(
            df_periodo,
            servicios,
            clientes,
            mensual_periodo
        )

        for conclusion in conclusiones:
            st.info(conclusion)

        clientes_nuevos = clientes[
            "Cliente nuevo"
        ].sum()

        clientes_recurrentes = (
            clientes["Visitas"] > 1
        ).sum()

        cliente_mayor_gasto = clientes.iloc[0]["Cliente"]

        gasto_mayor_cliente = clientes.iloc[0]["Gasto"]


        col1, col2, col3 = st.columns(3)

        col1.metric(
            "🆕 Clientes con 1 visita",
            clientes_nuevos
        )

        col2.metric(
            "🔄 Clientes recurrentes",
            clientes_recurrentes
        )

        col3.metric(
            "🏆 Cliente con mayor gasto",
            cliente_mayor_gasto,
            f"{gasto_mayor_cliente:.2f} €"
        )


        clientes["Primera_visita"] = (
            clientes["Primera_visita"]
            .dt.strftime("%d/%m/%Y")
        )

        clientes["Ultima_visita"] = (
            clientes["Ultima_visita"]
            .dt.strftime("%d/%m/%Y")
        )


        st.dataframe(
            clientes,
            use_container_width=True,
            hide_index=True
        )


        # =========================================================
        # MÉTODOS DE PAGO
        # =========================================================

        st.divider()

        st.subheader("💳 Métodos de pago")

        pagos = analizar_pagos(df_periodo)

        grafico_pagos = px.pie(
            pagos,
            names="Metodo pago",
            values="Ingresos",
            title="Distribución de ingresos por método de pago"
        )

        st.plotly_chart(
            grafico_pagos,
            use_container_width=True
        )


        # =========================================================
        # PDF
        # =========================================================

        st.divider()

        st.subheader("📄 Informe")

        # IMPORTANTE:
        # Para el PDF usamos df_periodo.
        # Así el informe corresponde al mes seleccionado.

        mensual_pdf = ingresos_por_mes(df_periodo)


        pdf = generar_pdf(
            resumen,
            mensual_pdf,
            servicios,
            clientes,
            pagos,
            periodo_seleccionado,
            comparacion,
            conclusiones
        )


        # Nombre del archivo

        if periodo_seleccionado == "Todo el periodo":
            nombre_pdf = "Informe_Todo_el_periodo.pdf"
        else:
            nombre_pdf = f"Informe_{periodo_seleccionado}.pdf"

        st.download_button(
            label="⬇️ Descargar informe PDF",
            data=pdf.getvalue(),
            file_name=nombre_pdf,
            mime="application/pdf",
            key="descargar_informe_pdf"
        )


    except Exception as error:

        st.error(
            f"No se pudo analizar el archivo: {error}"
        )