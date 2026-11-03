from contextlib import asynccontextmanager

from fastapi import FastAPI

from app.database import crear_tablas
from app.routers import autores, libros, prestamos, socios


@asynccontextmanager
async def lifespan(app: FastAPI):
    crear_tablas()
    yield


app = FastAPI(title="Biblioteca", version="1.0.0", lifespan=lifespan)
app.include_router(autores.router)
app.include_router(libros.router)
app.include_router(socios.router)
app.include_router(prestamos.router)
