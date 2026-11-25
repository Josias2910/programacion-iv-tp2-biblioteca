from datetime import date, timedelta

from fastapi import HTTPException
from sqlmodel import Session

from app.models import Prestamo, PrestamoCreate
from app.repositories import libros, prestamos, socios


def hoy() -> date:
    return date.today()


def registrar_prestamo(session: Session, datos: PrestamoCreate) -> Prestamo:
    socio = socios.obtener(session, datos.socio_id)
    libro = libros.obtener(session, datos.libro_id)
    if socio is None or libro is None:
        raise HTTPException(404, "Socio o libro inexistente")
    if not socio.activo:
        raise HTTPException(403, "El socio está inactivo")

    activos = prestamos.listar_del_socio(session, datos.socio_id, activos=True)
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
    return prestamos.guardar_con_stock(session, prestamo, libro)


def registrar_devolucion(session: Session, prestamo_id: int) -> Prestamo:
    prestamo = prestamos.obtener(session, prestamo_id)
    if prestamo is None:
        raise HTTPException(404, "Préstamo inexistente")
    if prestamo.fecha_devolucion is not None:
        raise HTTPException(409, "El préstamo ya fue devuelto")

    libro = prestamos.libro_del_prestamo(prestamo)
    prestamo.fecha_devolucion = hoy()
    atraso = max(0, (prestamo.fecha_devolucion - prestamo.fecha_vencimiento).days)
    prestamo.multa = atraso * 100
    libro.stock += 1
    return prestamos.guardar_con_stock(session, prestamo, libro)
