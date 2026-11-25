import pytest
from sqlalchemy import event
from sqlmodel import Session


@pytest.mark.parametrize("es_devolucion", [False, True])
def test_error_de_guardado_no_cambia_stock_ni_prestamo(client, datos, es_devolucion):
    libro_url = f"/libros/{datos['libro_id']}"
    prestamos_url = f"/socios/{datos['socio_id']}/prestamos"
    prestamo = client.post("/prestamos", json=datos).json() if es_devolucion else None
    stock_antes = client.get(libro_url).json()["stock"]
    prestamos_antes = client.get(prestamos_url).json()

    def falla_despues_de_escribir(*_):
        raise RuntimeError("Fallo de guardado de prueba")

    event.listen(Session, "after_flush", falla_despues_de_escribir)
    try:
        with pytest.raises(RuntimeError, match="Fallo de guardado de prueba"):
            if es_devolucion:
                client.post(f"/prestamos/{prestamo['id']}/devolucion")
            else:
                client.post("/prestamos", json=datos)
    finally:
        event.remove(Session, "after_flush", falla_despues_de_escribir)

    assert client.get(libro_url).json()["stock"] == stock_antes
    assert client.get(prestamos_url).json() == prestamos_antes
