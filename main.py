from fastapi import FastAPI
import os
import pandas as pd
app = FastAPI()

def cargar_cotizaciones():
    ruta = os.path.join(os.path.dirname(__file__), "cotizaciones.xlsx")
    df = pd.read_excel(ruta)
    df.columns = df.columns.str.strip().str.lower().str.replace(' ', '_')
    return df.to_dict('records')

# Ruta raíz
@app.get("/")
def inicio():
    return {"mensaje": "¡API de cotizaciones activa!"}

# Endpoint de cotización
@app.post("/cotizacion")
def cotizar(datos: dict):
    nombre = datos.get("nombre", "Cliente")
    marca = datos.get("marca", "").strip().title()
    modelo = datos.get("modelo", "").strip().title()
    anio = str(datos.get("año", ""))

    cotizaciones = cargar_cotizaciones()

    for auto in cotizaciones:
        if (auto["marca"].title() == marca and
            auto["modelo"].title() == modelo and
            str (int(auto["año"])) == anio):
            precio = auto["precio_mensual"]
            return {
                "encontrado": True,
                "nombre": nombre,
                "auto": f"{marca} {modelo} {anio}",
                "precio_mensual": precio,
                "mensaje": f"Hola {nombre}, tu cotización para un {marca} {modelo} {anio} es de ${precio}/mes. ¿Deseas continuar con un agente?"
            }

    return {
        "encontrado": False,
        "mensaje": f"Lo sentimos {nombre}, no encontramos cotización para {marca} {modelo} {anio}. ¿Deseas hablar con un agente?"
    }
