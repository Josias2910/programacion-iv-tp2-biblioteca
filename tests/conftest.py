from datetime import date

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import event
from sqlmodel import Session, SQLModel, create_engine
from sqlmodel.pool import StaticPool

from app.database import get_session
from app import main
from app.main import app
from app.services import prestamos


@pytest.fixture
def client(monkeypatch):
    engine = create_engine("sqlite://", connect_args={"check_same_thread": False}, poolclass=StaticPool)

    @event.listens_for(engine, "connect")
    def claves_foraneas(connection, _):
        connection.execute("PRAGMA foreign_keys=ON")

    SQLModel.metadata.create_all(engine)

    def session_de_prueba():
        with Session(engine) as session:
            yield session

    app.dependency_overrides[get_session] = session_de_prueba
    monkeypatch.setattr(prestamos, "hoy", lambda: date(2026, 10, 1))
    monkeypatch.setattr(main, "crear_tablas", lambda: None)
    with TestClient(app) as test_client:
        yield test_client
    app.dependency_overrides.clear()
    engine.dispose()


@pytest.fixture
def datos(client):
    socio = client.post("/socios", json={"nombre": "Ana", "email": "ana@example.com"}).json()
    libro = client.post("/libros", json={"titulo": "El principito", "isbn": "9780000000001", "stock": 5, "anio": 1943}).json()
    return {"socio_id": socio["id"], "libro_id": libro["id"]}
