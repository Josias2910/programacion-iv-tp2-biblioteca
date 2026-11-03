from fastapi import APIRouter, Depends, HTTPException, Response
from sqlalchemy.exc import IntegrityError
from sqlmodel import Session, select

from app.database import get_session
from app.models import Libro, LibroBase, LibroRead, Prestamo
from app.routers.autores import buscar_autor

router = APIRouter(prefix="/libros", tags=["Libros"])


def buscar_libro(session: Session, libro_id: int) -> Libro:
    libro = session.get(Libro, libro_id)
    if libro is None:
        raise HTTPException(404, "Libro inexistente")
    return libro


def guardar_libro(session: Session, libro: Libro):
    session.add(libro)
    try:
        session.commit()
    except IntegrityError:
        session.rollback()
        raise HTTPException(409, "Ya existe un libro con ese ISBN")
    session.refresh(libro)
    return libro


@router.post("", response_model=LibroRead, status_code=201)
def crear_libro(datos: LibroBase, session: Session = Depends(get_session)):
    return guardar_libro(session, Libro.model_validate(datos))


@router.get("", response_model=list[LibroRead])
def listar_libros(disponibles: bool | None = None, session: Session = Depends(get_session)):
    consulta = select(Libro).order_by(Libro.id)
    if disponibles is True:
        consulta = consulta.where(Libro.stock > 0)
    elif disponibles is False:
        consulta = consulta.where(Libro.stock == 0)
    return session.exec(consulta).all()


@router.get("/{libro_id}", response_model=LibroRead)
def obtener_libro(libro_id: int, session: Session = Depends(get_session)):
    return buscar_libro(session, libro_id)


@router.put("/{libro_id}", response_model=LibroRead)
def modificar_libro(libro_id: int, datos: LibroBase, session: Session = Depends(get_session)):
    libro = buscar_libro(session, libro_id)
    libro.sqlmodel_update(datos.model_dump())
    return guardar_libro(session, libro)


@router.delete("/{libro_id}", status_code=204)
def eliminar_libro(libro_id: int, session: Session = Depends(get_session)):
    libro = buscar_libro(session, libro_id)
    if session.exec(select(Prestamo).where(Prestamo.libro_id == libro_id)).first():
        raise HTTPException(409, "No se puede eliminar un libro con préstamos registrados")
    session.delete(libro)
    session.commit()
    return Response(status_code=204)


@router.post("/{libro_id}/autores/{autor_id}", response_model=LibroRead)
def asociar_autor(libro_id: int, autor_id: int, session: Session = Depends(get_session)):
    libro = buscar_libro(session, libro_id)
    autor = buscar_autor(session, autor_id)
    if autor in libro.autores:
        raise HTTPException(409, "El autor ya está asociado al libro")
    libro.autores.append(autor)
    session.add(libro)
    session.commit()
    session.refresh(libro)
    return libro
