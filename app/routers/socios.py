from fastapi import APIRouter, Depends, HTTPException, Response
from sqlalchemy.exc import IntegrityError
from sqlmodel import Session, select

from app.database import get_session
from app.models import Prestamo, PrestamoRead, Socio, SocioBase, SocioRead

router = APIRouter(prefix="/socios", tags=["Socios"])


def buscar_socio(session: Session, socio_id: int) -> Socio:
    socio = session.get(Socio, socio_id)
    if socio is None:
        raise HTTPException(404, "Socio inexistente")
    return socio


def guardar_socio(session: Session, socio: Socio):
    session.add(socio)
    try:
        session.commit()
    except IntegrityError:
        session.rollback()
        raise HTTPException(409, "Ya existe un socio con ese email")
    session.refresh(socio)
    return socio


@router.post("", response_model=SocioRead, status_code=201)
def crear_socio(datos: SocioBase, session: Session = Depends(get_session)):
    return guardar_socio(session, Socio.model_validate(datos))


@router.get("", response_model=list[SocioRead])
def listar_socios(session: Session = Depends(get_session)):
    return session.exec(select(Socio).order_by(Socio.id)).all()


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
    if session.exec(select(Prestamo).where(Prestamo.socio_id == socio_id)).first():
        raise HTTPException(409, "No se puede eliminar un socio con préstamos registrados")
    session.delete(socio)
    session.commit()
    return Response(status_code=204)


@router.get("/{socio_id}/prestamos", response_model=list[PrestamoRead])
def prestamos_del_socio(socio_id: int, activos: bool | None = None, session: Session = Depends(get_session)):
    buscar_socio(session, socio_id)
    consulta = select(Prestamo).where(Prestamo.socio_id == socio_id).order_by(Prestamo.id)
    if activos is True:
        consulta = consulta.where(Prestamo.fecha_devolucion.is_(None))
    elif activos is False:
        consulta = consulta.where(Prestamo.fecha_devolucion.is_not(None))
    return session.exec(consulta).all()
