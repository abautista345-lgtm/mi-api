from fastapi import FastAPI

app = FastAPI()

# Ruta raíz
@app.get("/")
def inicio():
    return {"mensaje": "¡Mi API está viva!"}

# Ruta con parámetro
@app.get("/saludo")
def saludar(nombre: str = "mundo"):
    return {"saludo": f"Hola, {nombre}!"}
