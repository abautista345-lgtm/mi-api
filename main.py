from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
import os
import pandas as pd

cotizaciones_cache = []

@asynccontextmanager
async def lifespan(app: FastAPI):
    global cotizaciones_cache
    ruta = os.path.join(os.path.dirname(__file__), "cotizaciones.xlsx")
    df = pd.read_excel(ruta)
    df.columns = df.columns.str.strip().str.lower().str.replace(' ', '_')
    cotizaciones_cache = df.to_dict('records')
    yield

app = FastAPI(lifespan=lifespan)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

AIVO_TOKEN = os.getenv("AIVO_TOKEN", "")

def token_valido(request: Request) -> bool:
    if not AIVO_TOKEN:
        return True
    auth = request.headers.get("Authorization", "")
    return auth == f"Bearer {AIVO_TOKEN}" or auth == AIVO_TOKEN

@app.get("/")
def inicio():
    return {"mensaje": "¡API de cotizaciones activa!"}

@app.post("/cotizacion")
async def cotizar(request: Request):
    if not token_valido(request):
        return {"text": "No autorizado. Token inválido.", "encontrado": False}

    try:
        datos = await request.json()
    except Exception:
        return {"text": "No pude leer los datos enviados. Verifica el formato JSON.", "encontrado": False}

    nombre = datos.get("nombre", "Cliente")
    marca = datos.get("marca", "").strip().title()
    modelo = datos.get("modelo", "").strip().title()
    anio = str(datos.get("año", ""))

    for auto in cotizaciones_cache:
        if (auto["marca"].title() == marca and
                auto["modelo"].title() == modelo and
                str(int(auto["año"])) == anio):
            precio = auto["precio_mensual"]
            mensaje = f"Hola {nombre}, tu cotización para un {marca} {modelo} {anio} es de ${precio}/mes. ¿Deseas continuar con un agente?"
            return {
                "text": mensaje,
                "encontrado": True,
                "nombre": nombre,
                "auto": f"{marca} {modelo} {anio}",
                "precio_mensual": precio,
                "mensaje": mensaje,
            }

    mensaje = f"Lo sentimos {nombre}, no encontramos cotización para {marca} {modelo} {anio}. ¿Deseas hablar con un agente?"
    return {
        "text": mensaje,
        "encontrado": False,
        "mensaje": mensaje,
    }
