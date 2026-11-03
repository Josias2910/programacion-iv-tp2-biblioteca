from sqlalchemy import inspect
from sqlmodel import create_engine

from app import database
from app.services.prestamos import hoy


def test_crear_tablas_y_sesion(tmp_path, monkeypatch):
    engine = create_engine(f"sqlite:///{tmp_path / 'prueba.db'}")
    monkeypatch.setattr(database, "engine", engine)
    database.crear_tablas()
    assert set(inspect(engine).get_table_names()) == {"autor", "libro", "libroautor", "socio", "prestamo"}
    sesiones = database.get_session()
    session = next(sesiones)
    assert session.bind is engine
    sesiones.close()
    engine.dispose()


def test_fecha_actual():
    from datetime import date
    assert hoy() == date.today()
