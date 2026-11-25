from fastapi import APIRouter, Depends, HTTPException, Response
from sqlmodel import Session

from app.database import get_session
from app.models import PrestamoRead, Socio, SocioBase, SocioRead
from app.repositories import prestamos, socios

router = APIRouter(prefix="/socios", tags=["Socios"])


def buscar_socio(session: Session, socio_id: int) -> Socio:
    socio = socios.obtener(session, socio_id)
    if socio is None:
        raise HTTPException(404, "Socio inexistente")
    return socio


def guardar_socio(session: Session, socio: Socio):
    try:
        return socios.guardar(session, socio)
    except socios.EmailRepetido:
        raise HTTPException(409, "Ya existe un socio con ese email")


@router.post("", response_model=SocioRead, status_code=201)
def crear_socio(datos: SocioBase, session: Session = Depends(get_session)):
    return guardar_socio(session, Socio.model_validate(datos))


@router.get("", response_model=list[SocioRead])
def listar_socios(session: Session = Depends(get_session)):
    return socios.listar(session)


@router.get("/{socio_id}", response_model=SocioRead)
def obtener_socio(socio_id: int, session: Session = Depends(get_session)):
    return buscar_socio(session, socio_id)


@router.put("/{socio_id}", response_model=SocioRead)
def modificar_socio(socio_id: int, datos: SocioBase, session: Session = Depends(get_session)):
    socio = buscar_socio(session, socio_id)
    socio.sqlmodel_update(datos.model_dump())
    return guardar_socio(session, socio)


@router.delete("/{socio_id}", status_code=204)
def eliminar_socio(socio_id: int, session: Session = Depends(get_session)):
    socio = buscar_socio(session, socio_id)
    if prestamos.existe_para_socio(session, socio_id):
        raise HTTPException(409, "No se puede eliminar un socio con préstamos registrados")
    socios.eliminar(session, socio)
    return Response(status_code=204)


@router.get("/{socio_id}/prestamos", response_model=list[PrestamoRead])
def prestamos_del_socio(socio_id: int, activos: bool | None = None, session: Session = Depends(get_session)):
    buscar_socio(session, socio_id)
    return prestamos.listar_del_socio(session, socio_id, activos)
