import pytest


def libro(isbn="ISBN-1", stock=2):
    return {"titulo": "Rayuela", "isbn": isbn, "stock": stock, "anio": 1963}


def test_crud_autores(client):
    r = client.post("/autores", json={"nombre": "Julio Cortázar", "nacionalidad": "Argentina"})
    assert r.status_code == 201
    autor_id = r.json()["id"]
    assert client.get("/autores").json() == [r.json()]
    assert client.get(f"/autores/{autor_id}").json() == r.json()
    r = client.put(f"/autores/{autor_id}", json={"nombre": "Cortázar", "nacionalidad": "Argentina"})
    assert r.status_code == 200
    assert r.json()["nombre"] == "Cortázar"
    assert client.delete(f"/autores/{autor_id}").status_code == 204
    assert client.get(f"/autores/{autor_id}").status_code == 404


def test_crud_libros_y_filtro(client):
    r = client.post("/libros", json=libro())
    assert r.status_code == 201
    libro_id = r.json()["id"]
    assert client.get(f"/libros/{libro_id}").json() == r.json()
    client.post("/libros", json=libro("ISBN-2", 0))
    assert len(client.get("/libros").json()) == 2
    assert len(client.get("/libros?disponibles=true").json()) == 1
    assert len(client.get("/libros?disponibles=false").json()) == 1
    r = client.put(f"/libros/{libro_id}", json={**libro(), "titulo": "Otro título"})
    assert r.status_code == 200
    assert r.json()["titulo"] == "Otro título"
    assert client.delete(f"/libros/{libro_id}").status_code == 204
    assert client.get(f"/libros/{libro_id}").status_code == 404


def test_isbn_duplicado_al_crear_y_modificar(client):
    client.post("/libros", json=libro())
    assert client.post("/libros", json=libro()).status_code == 409
    otro = client.post("/libros", json=libro("ISBN-2")).json()
    assert client.put(f"/libros/{otro['id']}", json=libro()).status_code == 409
    assert client.get(f"/libros/{otro['id']}").json()["isbn"] == "ISBN-2"


def test_relacion_muchos_a_muchos(client):
    a = client.post("/autores", json={"nombre": "Autor uno", "nacionalidad": "Argentina"}).json()
    b = client.post("/autores", json={"nombre": "Autor dos", "nacionalidad": "Uruguay"}).json()
    l1 = client.post("/libros", json=libro()).json()
    l2 = client.post("/libros", json=libro("ISBN-2")).json()
    assert client.post(f"/libros/{l1['id']}/autores/{a['id']}").status_code == 200
    assert client.post(f"/libros/{l1['id']}/autores/{b['id']}").status_code == 200
    assert client.post(f"/libros/{l2['id']}/autores/{a['id']}").status_code == 200
    assert len(client.get(f"/libros/{l1['id']}").json()["autores"]) == 2
    assert client.post(f"/libros/{l1['id']}/autores/{a['id']}").status_code == 409
    assert client.post(f"/libros/{l1['id']}/autores/999").status_code == 404
    assert client.post(f"/libros/999/autores/{a['id']}").status_code == 404
    assert client.delete(f"/autores/{a['id']}").status_code == 204
    assert len(client.get(f"/libros/{l1['id']}").json()["autores"]) == 1
    assert client.delete(f"/libros/{l1['id']}").status_code == 204
    assert client.get(f"/autores/{b['id']}").status_code == 200


def test_crud_socios(client):
    datos = {"nombre": "Ana", "email": "ana@example.com"}
    r = client.post("/socios", json=datos)
    assert r.status_code == 201
    socio_id = r.json()["id"]
    assert client.get("/socios").json() == [r.json()]
    assert client.get(f"/socios/{socio_id}").json() == r.json()
    r = client.put(f"/socios/{socio_id}", json={**datos, "activo": False})
    assert r.status_code == 200
    assert r.json()["activo"] is False
    assert client.delete(f"/socios/{socio_id}").status_code == 204
    assert client.get(f"/socios/{socio_id}").status_code == 404


def test_email_duplicado_al_crear_y_modificar(client):
    datos = {"nombre": "Ana", "email": "ana@example.com"}
    client.post("/socios", json=datos)
    assert client.post("/socios", json=datos).status_code == 409
    otro = client.post("/socios", json={"nombre": "Juan", "email": "juan@example.com"}).json()
    assert client.put(f"/socios/{otro['id']}", json=datos).status_code == 409
    assert client.get(f"/socios/{otro['id']}").json()["email"] == "juan@example.com"


@pytest.mark.parametrize("ruta,datos", [
    ("/autores", {"nombre": "", "nacionalidad": "Argentina"}),
    ("/libros", libro(stock=-1)),
    ("/libros", {**libro(), "isbn": ""}),
    ("/libros", {**libro(), "anio": 0}),
    ("/socios", {"nombre": "Ana", "email": "no-es-email"}),
    ("/prestamos", {"socio_id": 0, "libro_id": 1}),
])
def test_datos_invalidos(client, ruta, datos):
    assert client.post(ruta, json=datos).status_code == 422


@pytest.mark.parametrize("ruta,datos", [
    ("/autores", {"nombre": "Ana", "nacionalidad": "Argentina"}),
    ("/libros", libro()),
    ("/socios", {"nombre": "Ana", "email": "ana@example.com"}),
])
def test_recurso_inexistente(client, ruta, datos):
    assert client.get(f"{ruta}/999").status_code == 404
    assert client.put(f"{ruta}/999", json=datos).status_code == 404
    assert client.delete(f"{ruta}/999").status_code == 404
