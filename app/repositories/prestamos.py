from sqlmodel import Session, select

from app.models import Libro, Prestamo
from app.repositories import persistencia


def obtener(session: Session, prestamo_id: int) -> Prestamo | None:
    return session.get(Prestamo, prestamo_id)


def libro_del_prestamo(prestamo: Prestamo) -> Libro:
    return prestamo.libro


def listar_del_socio(session: Session, socio_id: int, activos: bool | None = None):
    consulta = select(Prestamo).where(Prestamo.socio_id == socio_id).order_by(Prestamo.id)
    if activos is True:
        consulta = consulta.where(Prestamo.fecha_devolucion.is_(None))
    elif activos is False:
        consulta = consulta.where(Prestamo.fecha_devolucion.is_not(None))
    return session.exec(consulta).all()


def existe_para_socio(session: Session, socio_id: int) -> bool:
    consulta = select(Prestamo.id).where(Prestamo.socio_id == socio_id).limit(1)
    return session.exec(consulta).first() is not None


def existe_para_libro(session: Session, libro_id: int) -> bool:
    consulta = select(Prestamo.id).where(Prestamo.libro_id == libro_id).limit(1)
    return session.exec(consulta).first() is not None


def guardar_con_stock(session: Session, prestamo: Prestamo, libro: Libro) -> Prestamo:
    persistencia.guardar(session, prestamo, libro)
    return prestamo
