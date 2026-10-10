import pandas as pd


COLUMNAS_REQUERIDAS = [
    "Fecha",
    "Cliente",
    "Servicio",
    "Precio",
    "Duracion min",
    "Metodo pago"
]


def cargar_excel(archivo):
    df = pd.read_excel(archivo)

    columnas_faltantes = [
        columna
        for columna in COLUMNAS_REQUERIDAS
        if columna not in df.columns
    ]

    if columnas_faltantes:
        raise ValueError(
            f"Faltan estas columnas: {', '.join(columnas_faltantes)}"
        )

    df["Fecha"] = pd.to_datetime(df["Fecha"], errors="coerce")
    df["Precio"] = pd.to_numeric(df["Precio"], errors="coerce")
    df["Duracion min"] = pd.to_numeric(
        df["Duracion min"],
        errors="coerce"
    )

    df = df.dropna(
        subset=[
            "Fecha",
            "Precio",
            "Duracion min"
        ]
    )

    return df


def calcular_resumen(df):

    facturacion = df["Precio"].sum()

    servicios = len(df)

    ticket_medio = df["Precio"].mean()

    horas = df["Duracion min"].sum() / 60

    ingreso_hora = (
        facturacion / horas
        if horas > 0
        else 0
    )

    clientes = df["Cliente"].nunique()

    return {
        "facturacion": facturacion,
        "servicios": servicios,
        "ticket_medio": ticket_medio,
        "horas": horas,
        "ingreso_hora": ingreso_hora,
        "clientes": clientes
    }


def ingresos_por_mes(df):

    resultado = (
        df.groupby(
            df["Fecha"].dt.to_period("M")
        )["Precio"]
        .sum()
        .reset_index()
    )

    resultado["Fecha"] = resultado["Fecha"].astype(str)

    resultado = resultado.rename(
        columns={
            "Fecha": "Mes",
            "Precio": "Ingresos"
        }
    )

    return resultado


def analizar_servicios(df):

    resultado = (
        df.groupby("Servicio")
        .agg(
            Ventas=("Servicio", "count"),
            Ingresos=("Precio", "sum"),
            Minutos=("Duracion min", "sum")
        )
        .reset_index()
    )

    resultado["Horas"] = resultado["Minutos"] / 60

    resultado["Euros por hora"] = (
        resultado["Ingresos"] / resultado["Horas"]
    )

    return resultado.sort_values(
        "Ingresos",
        ascending=False
    )


def analizar_clientes(df):

    resultado = (
        df.groupby("Cliente")
        .agg(
            Visitas=("Cliente", "count"),
            Gasto=("Precio", "sum"),
            Primera_visita=("Fecha", "min"),
            Ultima_visita=("Fecha", "max")
        )
        .reset_index()
    )

    resultado["Cliente nuevo"] = resultado["Visitas"] == 1

    resultado["Gasto"] = resultado["Gasto"].round(2)

    return resultado.sort_values(
        "Gasto",
        ascending=False
    )


def analizar_pagos(df):

    resultado = (
        df.groupby("Metodo pago")["Precio"]
        .sum()
        .reset_index()
    )

    resultado = resultado.rename(
        columns={
            "Precio": "Ingresos"
        }
    )

    return resultado

def comparar_meses(df, mes_actual, mes_anterior):

    df = df.copy()

    df["Mes"] = df["Fecha"].dt.to_period("M")

    actual = df[df["Mes"] == mes_actual]
    anterior = df[df["Mes"] == mes_anterior]

    def calcular_datos(datos):

        facturacion = datos["Precio"].sum()
        servicios = len(datos)
        ticket = datos["Precio"].mean()

        horas = datos["Duracion min"].sum() / 60

        ingreso_hora = (
            facturacion / horas
            if horas > 0
            else 0
        )

        return {
            "Facturación": facturacion,
            "Servicios": servicios,
            "Ticket medio": ticket,
            "Horas": horas,
            "€/hora": ingreso_hora
        }

    datos_actual = calcular_datos(actual)
    datos_anterior = calcular_datos(anterior)

    comparacion = []

    for indicador in datos_actual:

        valor_actual = datos_actual[indicador]
        valor_anterior = datos_anterior[indicador]

        if valor_anterior != 0:
            cambio = (
                (valor_actual - valor_anterior)
                / valor_anterior
            ) * 100
        else:
            cambio = 0

        comparacion.append({
            "Indicador": indicador,
            "Mes anterior": valor_anterior,
            "Mes actual": valor_actual,
            "Cambio %": cambio
        })

    return pd.DataFrame(comparacion)

def generar_conclusiones(df, servicios, clientes, mensual):
    """
    Genera conclusiones automáticas a partir de las ventas.
    """

    conclusiones = []

    if df.empty:
        return ["No hay datos suficientes para generar conclusiones."]

    # 1. Servicio con mayor facturación
    if not servicios.empty:
        servicio_top = servicios.loc[
            servicios["Ingresos"].idxmax()
        ]

        conclusiones.append(
            f"El servicio que mas factura es "
            f"{servicio_top['Servicio']}, con "
            f"{servicio_top['Ingresos']:.2f} €."
        )

    # 2. Servicio más vendido
    if not servicios.empty:
        servicio_mas_vendido = servicios.loc[
            servicios["Ventas"].idxmax()
        ]

        conclusiones.append(
            f"El servicio más vendido es "
            f"{servicio_mas_vendido['Servicio']}, "
            f"con {int(servicio_mas_vendido['Ventas'])} ventas."
        )

    # 3. Servicio con mayor ingreso por hora
    if not servicios.empty:
        servicios_validos = servicios[
            servicios["Horas"] > 0
        ]

        if not servicios_validos.empty:
            servicio_rentable = servicios_validos.loc[
                servicios_validos["Euros por hora"].idxmax()
            ]

            conclusiones.append(
                f"El servicio con mayor ingreso por hora es "
                f"{servicio_rentable['Servicio']}, con "
                f"{servicio_rentable['Euros por hora']:.2f} €/h."
            )

    # 4. Fidelización de clientes
    if not clientes.empty:
        total_clientes = len(clientes)

        clientes_recurrentes = (
            clientes["Visitas"] > 1
        ).sum()

        porcentaje_recurrentes = (
            clientes_recurrentes / total_clientes * 100
        )

        conclusiones.append(
            f"El {porcentaje_recurrentes:.1f}% de los clientes "
            f"registrados en el periodo ha realizado mas de una visita."
        )

    # 5. Evolución de la facturación
    if len(mensual) >= 2:
        mensual_ordenado = mensual.sort_values("Mes")

        ingresos_actuales = mensual_ordenado.iloc[-1]["Ingresos"]
        ingresos_anteriores = mensual_ordenado.iloc[-2]["Ingresos"]

        if ingresos_anteriores > 0:
            variacion = (
                (ingresos_actuales - ingresos_anteriores)
                / ingresos_anteriores
            ) * 100

            if variacion > 0:
                mensaje = (
                    f"La facturación aumentó un "
                    f"{variacion:.1f}% respecto al mes anterior."
                )

            elif variacion < 0:
                mensaje = (
                    f"La facturacilon disminuyo un "
                    f"{abs(variacion):.1f}% respecto al mes anterior."
                )

            else:
                mensaje = (
                    "La facturación se mantuvo igual que el mes anterior."
                )

            conclusiones.append(mensaje)

        elif ingresos_actuales > 0:
            conclusiones.append(
                "El mes anterior no registro ingresos, "
                "por lo que no se puede calcular una variación porcentual."
            )

    return conclusiones