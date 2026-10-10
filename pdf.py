from reportlab.lib import colors
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import cm
from reportlab.lib.enums import TA_CENTER

from reportlab.platypus import (
    SimpleDocTemplate,
    Paragraph,
    Spacer,
    Table,
    TableStyle,
    Image,
    PageBreak
)

from io import BytesIO
from datetime import datetime

import plotly.express as px


def crear_grafico_ingresos(mensual):

    grafico = px.bar(
        mensual,
        x="Mes",
        y="Ingresos",
        title="Evolución de facturación",
        template="plotly_white"
    )

    grafico.update_layout(
        height=350,
        margin=dict(
            l=40,
            r=40,
            t=60,
            b=40
        )
    )

    imagen = BytesIO()

    grafico.write_image(
        imagen,
        format="png",
        width=1000,
        height=500
    )

    imagen.seek(0)

    return imagen


def generar_pdf(
    resumen,
    mensual,
    servicios,
    clientes,
    pagos,
    periodo_seleccionado,
    comparacion=None,
    conclusiones=None
):

    buffer = BytesIO()

    documento = SimpleDocTemplate(
    buffer,
    pagesize=A4,
    rightMargin=1.5 * cm,
    leftMargin=1.5 * cm,
    topMargin=1.5 * cm,
    bottomMargin=1.5 * cm,
    title=f"Beauty Business - Informe {periodo_seleccionado}",
    author="Beauty Business Dashboard",
    subject=f"Informe de rendimiento del negocio: {periodo_seleccionado}"
    )   

    estilos = getSampleStyleSheet()

    titulo = ParagraphStyle(
        "TituloPersonalizado",
        parent=estilos["Title"],
        fontSize=26,
        leading=32,
        alignment=TA_CENTER,
        spaceAfter=15
    )

    subtitulo = ParagraphStyle(
        "SubtituloPersonalizado",
        parent=estilos["Heading2"],
        fontSize=16,
        leading=20,
        alignment=TA_CENTER,
        spaceAfter=10
    )

    texto_centrado = ParagraphStyle(
        "TextoCentrado",
        parent=estilos["BodyText"],
        alignment=TA_CENTER,
        fontSize=11
    )

    texto = estilos["BodyText"]

    contenido = []

    # =========================================================
    # PORTADA
    # =========================================================

    contenido.append(
        Spacer(1, 3 * cm)
    )

    contenido.append(
        Paragraph(
            "BEAUTY BUSINESS",
            titulo
        )
    )

    contenido.append(
        Paragraph(
            "Informe de rendimiento",
            subtitulo
        )
    )

    contenido.append(
        Spacer(1, 1 * cm)
    )

    contenido.append(
        Paragraph(
            f"Periodo analizado: <b>{periodo_seleccionado}</b>",
            texto_centrado
        )
    )

    contenido.append(
        Spacer(1, 0.5 * cm)
    )

    fecha_generacion = datetime.now().strftime(
        "%d/%m/%Y"
    )

    contenido.append(
        Paragraph(
            f"Informe generado el {fecha_generacion}",
            texto_centrado
        )
    )

    contenido.append(
        Spacer(1, 3 * cm)
    )

    contenido.append(
        Paragraph(
            "Análisis de ventas, clientes y rendimiento del negocio",
            texto_centrado
        )
    )

    contenido.append(
        PageBreak()
    )

    # =========================================================
    # RESUMEN
    # =========================================================

    contenido.append(
        Paragraph(
            "Resumen del negocio",
            subtitulo
        )
    )

    datos_resumen = [
        ["Indicador", "Resultado"],

        [
            "Facturación",
            f"{resumen['facturacion']:.2f} €"
        ],

        [
            "Servicios realizados",
            str(resumen["servicios"])
        ],

        [
            "Clientes",
            str(resumen["clientes"])
        ],

        [
            "Ticket medio",
            f"{resumen['ticket_medio']:.2f} €"
        ],

        [
            "Horas trabajadas",
            f"{resumen['horas']:.2f} h"
        ],

        [
            "Ingreso por hora",
            f"{resumen['ingreso_hora']:.2f} €/h"
        ]
    ]

    tabla_resumen = Table(
        datos_resumen,
        colWidths=[
            9 * cm,
            7 * cm
        ]
    )

    tabla_resumen.setStyle(
        TableStyle([
            (
                "BACKGROUND",
                (0, 0),
                (-1, 0),
                colors.lightgrey
            ),

            (
                "FONTNAME",
                (0, 0),
                (-1, 0),
                "Helvetica-Bold"
            ),

            (
                "GRID",
                (0, 0),
                (-1, -1),
                0.5,
                colors.grey
            ),

            (
                "ALIGN",
                (1, 1),
                (1, -1),
                "RIGHT"
            ),

            (
                "BOTTOMPADDING",
                (0, 0),
                (-1, -1),
                8
            ),

            (
                "TOPPADDING",
                (0, 0),
                (-1, -1),
                8
            )
        ])
    )

    contenido.append(
        tabla_resumen
    )

    contenido.append(
        Spacer(1, 1 * cm)
    )

    # =========================================================
    # GRÁFICO DE INGRESOS
    # =========================================================

    contenido.append(
        Paragraph(
            "Evolución de facturación",
            subtitulo
        )
    )

    if not mensual.empty:

        imagen_grafico = crear_grafico_ingresos(
            mensual
        )

        imagen = Image(
            imagen_grafico,
            width=17 * cm,
            height=8.5 * cm
        )

        contenido.append(
            imagen
        )

    contenido.append(
        Spacer(1, 0.8 * cm)
    )

    # =========================================================
    # TABLA EVOLUCIÓN
    # =========================================================

    contenido.append(
        Paragraph(
            "Detalle mensual",
            subtitulo
        )
    )

    datos_mensuales = [
        ["Mes", "Ingresos"]
    ]

    for _, fila in mensual.iterrows():

        datos_mensuales.append([
            fila["Mes"],
            f"{fila['Ingresos']:.2f} €"
        ])

    tabla_mensual = Table(
        datos_mensuales,
        colWidths=[
            9 * cm,
            7 * cm
        ]
    )

    tabla_mensual.setStyle(
        TableStyle([
            (
                "BACKGROUND",
                (0, 0),
                (-1, 0),
                colors.lightgrey
            ),

            (
                "FONTNAME",
                (0, 0),
                (-1, 0),
                "Helvetica-Bold"
            ),

            (
                "GRID",
                (0, 0),
                (-1, -1),
                0.5,
                colors.grey
            ),

            (
                "ALIGN",
                (1, 1),
                (1, -1),
                "RIGHT"
            ),

            (
                "BOTTOMPADDING",
                (0, 0),
                (-1, -1),
                6
            ),

            (
                "TOPPADDING",
                (0, 0),
                (-1, -1),
                6
            )
        ])
    )

    contenido.append(
        tabla_mensual
    )

    contenido.append(
        PageBreak()
    )

    # =========================================================
    # COMPARACIÓN
    # =========================================================

    if comparacion is not None:

        contenido.append(
            Paragraph(
                "Comparación mensual",
                subtitulo
            )
        )

        datos_comparacion = [
            [
                "Indicador",
                "Anterior",
                "Actual",
                "Cambio"
            ]
        ]

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

            datos_comparacion.append([
                indicador,
                anterior_texto,
                actual_texto,
                f"{cambio:.1f}%"
            ])

        tabla_comparacion = Table(
            datos_comparacion,
            colWidths=[
                5 * cm,
                4 * cm,
                4 * cm,
                3 * cm
            ]
        )

        tabla_comparacion.setStyle(
            TableStyle([
                (
                    "BACKGROUND",
                    (0, 0),
                    (-1, 0),
                    colors.lightgrey
                ),

                (
                    "FONTNAME",
                    (0, 0),
                    (-1, 0),
                    "Helvetica-Bold"
                ),

                (
                    "GRID",
                    (0, 0),
                    (-1, -1),
                    0.5,
                    colors.grey
                ),

                (
                    "ALIGN",
                    (1, 1),
                    (-1, -1),
                    "RIGHT"
                ),

                (
                    "BOTTOMPADDING",
                    (0, 0),
                    (-1, -1),
                    5
                ),

                (
                    "TOPPADDING",
                    (0, 0),
                    (-1, -1),
                    5
                )
            ])
        )

        contenido.append(
            tabla_comparacion
        )

        contenido.append(
            Spacer(1, 1 * cm)
        )

    # =========================================================
    # SERVICIOS
    # =========================================================

    contenido.append(
        Paragraph(
            "Rendimiento de servicios",
            subtitulo
        )
    )

    datos_servicios = [
        [
            "Servicio",
            "Ventas",
            "Ingresos",
            "€/hora"
        ]
    ]

    for _, fila in servicios.iterrows():

        datos_servicios.append([
            fila["Servicio"],
            str(fila["Ventas"]),
            f"{fila['Ingresos']:.2f} €",
            f"{fila['Euros por hora']:.2f} €"
        ])

    tabla_servicios = Table(
        datos_servicios,
        colWidths=[
            6 * cm,
            3 * cm,
            4 * cm,
            3 * cm
        ]
    )

    tabla_servicios.setStyle(
        TableStyle([
            (
                "BACKGROUND",
                (0, 0),
                (-1, 0),
                colors.lightgrey
            ),

            (
                "FONTNAME",
                (0, 0),
                (-1, 0),
                "Helvetica-Bold"
            ),

            (
                "GRID",
                (0, 0),
                (-1, -1),
                0.5,
                colors.grey
            ),

            (
                "ALIGN",
                (1, 1),
                (-1, -1),
                "RIGHT"
            ),

            (
                "BOTTOMPADDING",
                (0, 0),
                (-1, -1),
                5
            ),

            (
                "TOPPADDING",
                (0, 0),
                (-1, -1),
                5
            )
        ])
    )

    contenido.append(
        tabla_servicios
    )

    contenido.append(
        Spacer(1, 1 * cm)
    )

    # =========================================================
    # CLIENTES
    # =========================================================

    contenido.append(
        Paragraph(
            "Clientes",
            subtitulo
        )
    )

    datos_clientes = [
        [
            "Cliente",
            "Visitas",
            "Gasto"
        ]
    ]

    clientes_pdf = clientes.head(10)

    for _, fila in clientes_pdf.iterrows():

        datos_clientes.append([
            fila["Cliente"],
            str(fila["Visitas"]),
            f"{fila['Gasto']:.2f} €"
        ])

    tabla_clientes = Table(
        datos_clientes,
        colWidths=[
            8 * cm,
            4 * cm,
            4 * cm
        ]
    )

    tabla_clientes.setStyle(
        TableStyle([
            (
                "BACKGROUND",
                (0, 0),
                (-1, 0),
                colors.lightgrey
            ),

            (
                "FONTNAME",
                (0, 0),
                (-1, 0),
                "Helvetica-Bold"
            ),

            (
                "GRID",
                (0, 0),
                (-1, -1),
                0.5,
                colors.grey
            ),

            (
                "ALIGN",
                (1, 1),
                (-1, -1),
                "RIGHT"
            ),

            (
                "BOTTOMPADDING",
                (0, 0),
                (-1, -1),
                5
            ),

            (
                "TOPPADDING",
                (0, 0),
                (-1, -1),
                5
            )
        ])
    )

    contenido.append(
        tabla_clientes
    )

    contenido.append(
        Spacer(1, 1 * cm)
    )

    # =========================================================
    # MÉTODOS DE PAGO
    # =========================================================

    contenido.append(
        Paragraph(
            "Métodos de pago",
            subtitulo
        )
    )

    datos_pagos = [
        [
            "Método",
            "Ingresos"
        ]
    ]

    for _, fila in pagos.iterrows():

        datos_pagos.append([
            fila["Metodo pago"],
            f"{fila['Ingresos']:.2f} €"
        ])

    tabla_pagos = Table(
        datos_pagos,
        colWidths=[
            9 * cm,
            7 * cm
        ]
    )

    tabla_pagos.setStyle(
        TableStyle([
            (
                "BACKGROUND",
                (0, 0),
                (-1, 0),
                colors.lightgrey
            ),

            (
                "FONTNAME",
                (0, 0),
                (-1, 0),
                "Helvetica-Bold"
            ),

            (
                "GRID",
                (0, 0),
                (-1, -1),
                0.5,
                colors.grey
            ),

            (
                "ALIGN",
                (1, 1),
                (1, -1),
                "RIGHT"
            ),

            (
                "BOTTOMPADDING",
                (0, 0),
                (-1, -1),
                5
            ),

            (
                "TOPPADDING",
                (0, 0),
                (-1, -1),
                5
            )
        ])
    )

    contenido.append(
        tabla_pagos
    )

    # =========================================================
# CONCLUSIONES AUTOMÁTICAS
# =========================================================

    if conclusiones:

        contenido.append(
            Spacer(1, 1 * cm)
        )

        contenido.append(
            Paragraph(
                "Conclusiones y oportunidades",
                subtitulo
            )
        )

        for conclusion in conclusiones:
            contenido.append(
                Paragraph(
                    conclusion,
                    texto
                )
            )
                    

            contenido.append(
                Spacer(1, 0.3 * cm)
            )
    # =========================================================
    # GENERAR
    # ========================================================

    documento.build(
        contenido
    )

    buffer.seek(0)

    return buffer