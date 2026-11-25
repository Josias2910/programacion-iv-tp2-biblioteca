from sqlmodel import Session, SQLModel


def guardar(session: Session, registro: SQLModel, *relacionados: SQLModel):
    try:
        session.add_all([registro, *relacionados])
        session.commit()
    except Exception:
        session.rollback()
        raise
    session.refresh(registro)


def eliminar(session: Session, registro: SQLModel):
    try:
        session.delete(registro)
        session.commit()
    except Exception:
        session.rollback()
        raise
