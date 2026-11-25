from sqlalchemy.exc import IntegrityError
from sqlmodel import Session, select

from app.models import Autor, Libro
from app.repositories import persistencia


class ISBNRepetido(Exception):
    pass


def obtener(session: Session, libro_id: int) -> Libro | None:
    return session.get(Libro, libro_id)


def listar(session: Session, disponibles: bool | None):
    consulta = select(Libro).order_by(Libro.id)
    if disponibles is True:
        consulta = consulta.where(Libro.stock > 0)
    elif disponibles is False:
        consulta = consulta.where(Libro.stock == 0)
    return session.exec(consulta).all()


def guardar(session: Session, libro: Libro) -> Libro:
    try:
        persistencia.guardar(session, libro)
    except IntegrityError as error:
        raise ISBNRepetido from error
    return libro


def eliminar(session: Session, libro: Libro):
    persistencia.eliminar(session, libro)


def asociar_autor(session: Session, libro: Libro, autor: Autor) -> bool:
    if autor in libro.autores:
        return False
    libro.autores.append(autor)
    persistencia.guardar(session, libro)
    return True
