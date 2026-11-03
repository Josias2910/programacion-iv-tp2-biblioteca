from datetime import date, timedelta

from fastapi import HTTPException
from sqlmodel import Session, select

from app.models import Libro, Prestamo, PrestamoCreate, Socio


def hoy() -> date:
    return date.today()


def registrar_prestamo(session: Session, datos: PrestamoCreate) -> Prestamo:
    socio = session.get(Socio, datos.socio_id)
    libro = session.get(Libro, datos.libro_id)
    if socio is None or libro is None:
        raise HTTPException(404, "Socio o libro inexistente")
    if not socio.activo:
        raise HTTPException(403, "El socio está inactivo")

    activos = session.exec(
        select(Prestamo).where(
            Prestamo.socio_id == socio.id, Prestamo.fecha_devolucion.is_(None)
        )
    ).all()
    if len(activos) >= 3:
        raise HTTPException(409, "El socio ya tiene tres préstamos activos")
    if libro.stock == 0:
        raise HTTPException(409, "El libro no tiene stock disponible")

    fecha = hoy()
    prestamo = Prestamo(
        socio_id=socio.id,
        libro_id=libro.id,
        fecha_prestamo=fecha,
        fecha_vencimiento=fecha + timedelta(days=14),
    )
    libro.stock -= 1
    session.add(libro)
    session.add(prestamo)
    session.commit()
    session.refresh(prestamo)
    return prestamo


def registrar_devolucion(session: Session, prestamo_id: int) -> Prestamo:
    prestamo = session.get(Prestamo, prestamo_id)
    if prestamo is None:
        raise HTTPException(404, "Préstamo inexistente")
    if prestamo.fecha_devolucion is not None:
        raise HTTPException(409, "El préstamo ya fue devuelto")

    prestamo.fecha_devolucion = hoy()
    atraso = max(0, (prestamo.fecha_devolucion - prestamo.fecha_vencimiento).days)
    prestamo.multa = atraso * 100
    prestamo.libro.stock += 1
    session.add(prestamo.libro)
    session.add(prestamo)
    session.commit()
    session.refresh(prestamo)
    return prestamo
