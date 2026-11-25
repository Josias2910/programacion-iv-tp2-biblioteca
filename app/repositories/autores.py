from sqlmodel import Session, select

from app.models import Autor
from app.repositories import persistencia


def obtener(session: Session, autor_id: int) -> Autor | None:
    return session.get(Autor, autor_id)


def listar(session: Session):
    return session.exec(select(Autor).order_by(Autor.id)).all()


def guardar(session: Session, autor: Autor) -> Autor:
    persistencia.guardar(session, autor)
    return autor


def eliminar(session: Session, autor: Autor):
    persistencia.eliminar(session, autor)
