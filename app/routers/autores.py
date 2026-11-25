from fastapi import APIRouter, Depends, HTTPException, Response
from sqlmodel import Session

from app.database import get_session
from app.models import Autor, AutorBase, AutorRead
from app.repositories import autores

router = APIRouter(prefix="/autores", tags=["Autores"])


def buscar_autor(session: Session, autor_id: int) -> Autor:
    autor = autores.obtener(session, autor_id)
    if autor is None:
        raise HTTPException(404, "Autor inexistente")
    return autor


@router.post("", response_model=AutorRead, status_code=201)
def crear_autor(datos: AutorBase, session: Session = Depends(get_session)):
    autor = Autor.model_validate(datos)
    return autores.guardar(session, autor)


@router.get("", response_model=list[AutorRead])
def listar_autores(session: Session = Depends(get_session)):
    return autores.listar(session)


@router.get("/{autor_id}", response_model=AutorRead)
def obtener_autor(autor_id: int, session: Session = Depends(get_session)):
    return buscar_autor(session, autor_id)


@router.put("/{autor_id}", response_model=AutorRead)
def modificar_autor(autor_id: int, datos: AutorBase, session: Session = Depends(get_session)):
    autor = buscar_autor(session, autor_id)
    autor.sqlmodel_update(datos.model_dump())
    return autores.guardar(session, autor)


@router.delete("/{autor_id}", status_code=204)
def eliminar_autor(autor_id: int, session: Session = Depends(get_session)):
    autor = buscar_autor(session, autor_id)
    autores.eliminar(session, autor)
    return Response(status_code=204)
