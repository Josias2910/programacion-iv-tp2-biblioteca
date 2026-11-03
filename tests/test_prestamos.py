from datetime import date

import pytest

from app.services import prestamos


def test_prestamo_descuenta_stock_y_vence_en_14_dias(client, datos):
    r = client.post("/prestamos", json=datos)
    assert r.status_code == 201
    prestamo = r.json()
    assert prestamo["socio_id"] == datos["socio_id"]
    assert prestamo["libro_id"] == datos["libro_id"]
    assert prestamo["fecha_prestamo"] == "2026-10-01"
    assert prestamo["fecha_vencimiento"] == "2026-10-15"
    assert prestamo["fecha_devolucion"] is None
    assert prestamo["multa"] == 0
    assert client.get(f"/libros/{datos['libro_id']}").json()["stock"] == 4


def test_maximo_tres_prestamos_activos(client, datos):
    for _ in range(3):
        assert client.post("/prestamos", json=datos).status_code == 201
    assert client.post("/prestamos", json=datos).status_code == 409
    assert client.get(f"/libros/{datos['libro_id']}").json()["stock"] == 2
    assert len(client.get(f"/socios/{datos['socio_id']}/prestamos").json()) == 3


def test_devolver_habilita_otro_prestamo(client, datos):
    prestamos_creados = [client.post("/prestamos", json=datos).json() for _ in range(3)]
    client.post(f"/prestamos/{prestamos_creados[0]['id']}/devolucion")
    assert client.post("/prestamos", json=datos).status_code == 201


def test_libro_sin_stock(client, datos):
    for _ in range(5):
        socio = client.post("/socios", json={"nombre": "Otro socio", "email": f"socio{_}@example.com"}).json()
        assert client.post("/prestamos", json={**datos, "socio_id": socio["id"]}).status_code == 201
    assert client.post("/prestamos", json=datos).status_code == 409
    assert client.get(f"/libros/{datos['libro_id']}").json()["stock"] == 0
    assert client.get(f"/socios/{datos['socio_id']}/prestamos").json() == []


def test_socio_inactivo(client, datos):
    client.put(f"/socios/{datos['socio_id']}", json={"nombre": "Ana", "email": "ana@example.com", "activo": False})
    assert client.post("/prestamos", json=datos).status_code == 403
    assert client.get(f"/libros/{datos['libro_id']}").json()["stock"] == 5


@pytest.mark.parametrize("fecha,multa", [(date(2026, 10, 10), 0), (date(2026, 10, 15), 0), (date(2026, 10, 18), 300)])
def test_devolucion_y_multa(client, datos, monkeypatch, fecha, multa):
    prestamo = client.post("/prestamos", json=datos).json()
    monkeypatch.setattr(prestamos, "hoy", lambda: fecha)
    r = client.post(f"/prestamos/{prestamo['id']}/devolucion")
    assert r.status_code == 200
    assert r.json()["multa"] == multa
    assert r.json()["fecha_devolucion"] == fecha.isoformat()
    assert client.get(f"/libros/{datos['libro_id']}").json()["stock"] == 5


def test_no_se_puede_devolver_dos_veces(client, datos):
    prestamo = client.post("/prestamos", json=datos).json()
    url = f"/prestamos/{prestamo['id']}/devolucion"
    assert client.post(url).status_code == 200
    assert client.post(url).status_code == 409
    assert client.get(f"/libros/{datos['libro_id']}").json()["stock"] == 5


def test_listar_prestamos_activos_e_historial(client, datos):
    p1 = client.post("/prestamos", json=datos).json()
    p2 = client.post("/prestamos", json=datos).json()
    client.post(f"/prestamos/{p1['id']}/devolucion")
    url = f"/socios/{datos['socio_id']}/prestamos"
    assert len(client.get(url).json()) == 2
    assert [p["id"] for p in client.get(url + "?activos=true").json()] == [p2["id"]]
    assert [p["id"] for p in client.get(url + "?activos=false").json()] == [p1["id"]]
    otro = client.post("/socios", json={"nombre": "Luis", "email": "luis@example.com"}).json()
    assert client.get(f"/socios/{otro['id']}/prestamos").json() == []


def test_prestamos_recursos_inexistentes(client, datos):
    assert client.post("/prestamos", json={**datos, "libro_id": 999}).status_code == 404
    assert client.post("/prestamos", json={**datos, "socio_id": 999}).status_code == 404
    assert client.post("/prestamos/999/devolucion").status_code == 404
    assert client.get("/socios/999/prestamos?activos=true").status_code == 404


def test_no_borrar_entidades_con_historial(client, datos):
    prestamo = client.post("/prestamos", json=datos).json()
    assert client.delete(f"/libros/{datos['libro_id']}").status_code == 409
    assert client.delete(f"/socios/{datos['socio_id']}").status_code == 409
    client.post(f"/prestamos/{prestamo['id']}/devolucion")
    assert client.delete(f"/socios/{datos['socio_id']}").status_code == 409
