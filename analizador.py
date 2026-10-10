import pandas as pd


archivo = "ventas.xlsm"


ventas = pd.read_excel(
    archivo,
    sheet_name="Ventas"
)
df = pd.DataFrame(ventas)
precio = df['Precio'].sum()
cantidaVentas = df['Precio'].count()
ventasProducto = df['Servicio'].value_counts().index[0]
PrecioPromedio = df['Precio'].mean().round()
Grupo = df.groupby('Servicio')['Precio'].sum().sort_values(ascending=False)
FrecuenciaServicio = df.groupby("Servicio")["Servicio"].count()

print(df)
print("El valor total es", precio,"€")
print("Cantidad de ventas:", cantidaVentas)
print("El servicio mas vendido:", ventasProducto)
print("Precio promedio:", PrecioPromedio)
print(Grupo)
print(FrecuenciaServicio)