from fastapi import APIRouter, Depends, HTTPException, Response
from sqlmodel import Session, select

from app.database import get_session
from app.models import Autor, AutorBase, AutorRead

router = APIRouter(prefix="/autores", tags=["Autores"])


def buscar_autor(session: Session, autor_id: int) -> Autor:
    autor = session.get(Autor, autor_id)
    if autor is None:
        raise HTTPException(404, "Autor inexistente")
    return autor


@router.post("", response_model=AutorRead, status_code=201)
def crear_autor(datos: AutorBase, session: Session = Depends(get_session)):
    autor = Autor.model_validate(datos)
    session.add(autor)
    session.commit()
    session.refresh(autor)
    return autor


@router.get("", response_model=list[AutorRead])
def listar_autores(session: Session = Depends(get_session)):
    return session.exec(select(Autor).order_by(Autor.id)).all()


@router.get("/{autor_id}", response_model=AutorRead)
def obtener_autor(autor_id: int, session: Session = Depends(get_session)):
    return buscar_autor(session, autor_id)


@router.put("/{autor_id}", response_model=AutorRead)
def modificar_autor(autor_id: int, datos: AutorBase, session: Session = Depends(get_session)):
    autor = buscar_autor(session, autor_id)
    autor.sqlmodel_update(datos.model_dump())
    session.add(autor)
    session.commit()
    session.refresh(autor)
    return autor


@router.delete("/{autor_id}", status_code=204)
def eliminar_autor(autor_id: int, session: Session = Depends(get_session)):
    autor = buscar_autor(session, autor_id)
    session.delete(autor)
    session.commit()
    return Response(status_code=204)
