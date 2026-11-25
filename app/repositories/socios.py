from sqlalchemy.exc import IntegrityError
from sqlmodel import Session, select

from app.models import Socio
from app.repositories import persistencia


class EmailRepetido(Exception):
    pass


def obtener(session: Session, socio_id: int) -> Socio | None:
    return session.get(Socio, socio_id)


def listar(session: Session):
    return session.exec(select(Socio).order_by(Socio.id)).all()


def guardar(session: Session, socio: Socio) -> Socio:
    try:
        persistencia.guardar(session, socio)
    except IntegrityError as error:
        raise EmailRepetido from error
    return socio


def eliminar(session: Session, socio: Socio):
    persistencia.eliminar(session, socio)
