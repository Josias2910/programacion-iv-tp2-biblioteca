from fastapi import APIRouter, Depends
from sqlmodel import Session

from app.database import get_session
from app.models import PrestamoCreate, PrestamoRead
from app.services.prestamos import registrar_devolucion, registrar_prestamo

router = APIRouter(prefix="/prestamos", tags=["Préstamos"])


@router.post("", response_model=PrestamoRead, status_code=201)
def crear_prestamo(datos: PrestamoCreate, session: Session = Depends(get_session)):
    return registrar_prestamo(session, datos)


@router.post("/{prestamo_id}/devolucion", response_model=PrestamoRead)
def devolver_prestamo(prestamo_id: int, session: Session = Depends(get_session)):
    return registrar_devolucion(session, prestamo_id)
