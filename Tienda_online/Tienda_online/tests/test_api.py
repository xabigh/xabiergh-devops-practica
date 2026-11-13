import os, sys
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

import pytest
from fastapi.testclient import TestClient
import main
from services.tienda_service import TiendaService


@pytest.fixture()
def client():
    main.tienda = TiendaService()  # estado limpio en cada test
    return TestClient(main.app)


def crear_cliente(c, email="ana@mail.com"):
    r = c.post("/usuarios", json={"nombre": "Ana", "email": email,
                                  "tipo": "cliente", "direccion_postal": "Calle A"})
    assert r.status_code == 201
    return r.json()


def crear_producto(c, **kw):
    datos = {"tipo": "generico", "nombre": "Cable", "precio": 10, "stock": 5}
    datos.update(kw)
    r = c.post("/productos", json=datos)
    assert r.status_code == 201, r.text
    return r.json()


def test_usuarios(client):
    u = crear_cliente(client)
    assert u["es_admin"] is False
    a = client.post("/usuarios", json={"nombre": "Admin", "email": "a@mail.com",
                                       "tipo": "administrador"}).json()
    assert a["es_admin"] is True
    assert client.get(f"/usuarios/{u['id']}").json() == u
    assert len(client.get("/usuarios").json()) == 2
    assert client.get("/usuarios/nope").status_code == 404
    assert client.post("/usuarios", json={"nombre": "X", "email": "ana@mail.com",
                       "tipo": "cliente", "direccion_postal": "c"}).status_code == 409
    assert client.post("/usuarios", json={"nombre": "X", "email": "x@mail.com",
                       "tipo": "cliente"}).status_code == 422
    assert client.post("/usuarios", json={"nombre": "X", "email": "mal",
                       "tipo": "administrador"}).status_code == 422
    assert client.post("/usuarios", json={"nombre": "X", "email": "x@mail.com",
                       "tipo": "otro"}).status_code == 422


def test_productos(client):
    e = crear_producto(client, tipo="electronico", nombre="Portátil",
                       precio=899.99, stock=10, meses_garantia=24)
    assert e["meses_garantia"] == 24 and e["talla"] is None
    r = crear_producto(client, tipo="ropa", nombre="Sudadera", talla="L", color="Gris")
    assert r["talla"] == "L"
    g = crear_producto(client)
    assert g["tipo"] == "generico"
    assert len(client.get("/productos").json()) == 3
    assert client.get(f"/productos/{g['id']}").status_code == 200
    base = {"nombre": "x", "precio": 1, "stock": 1}
    for extra in ({"tipo": "electronico"}, {"tipo": "ropa", "talla": "M"},
                  {"tipo": "generico", "color": "rojo"},
                  {"tipo": "ropa", "talla": "M", "color": "r", "meses_garantia": 3},
                  {"tipo": "generico", "precio": -1}):
        assert client.post("/productos", json={**base, **extra}).status_code == 422
    assert client.delete(f"/productos/{g['id']}").status_code == 204
    assert client.delete(f"/productos/{g['id']}").status_code == 404
    assert client.get(f"/productos/{g['id']}").status_code == 404


def test_pedidos(client):
    u = crear_cliente(client)
    p = crear_producto(client, precio=10.5, stock=5)
    r = client.post("/pedidos", json={"cliente_id": u["id"],
                                      "items": [{"producto_id": p["id"], "cantidad": 2}]})
    assert r.status_code == 201
    ped = r.json()
    assert ped["total"] == 21.0 and ped["items"][0]["subtotal"] == 21.0
    assert client.get(f"/productos/{p['id']}").json()["stock"] == 3

    hist = client.get(f"/usuarios/{u['id']}/pedidos").json()
    assert len(hist) == 1 and hist[0]["id"] == ped["id"]

    for items in ([{"producto_id": p["id"], "cantidad": 10}],
                  [{"producto_id": p["id"], "cantidad": 2},
                   {"producto_id": p["id"], "cantidad": 2}]):
        assert client.post("/pedidos", json={"cliente_id": u["id"],
                           "items": items}).status_code == 409
    assert client.get(f"/productos/{p['id']}").json()["stock"] == 3

    assert client.post("/pedidos", json={"cliente_id": "nope", "items": [
        {"producto_id": p["id"], "cantidad": 1}]}).status_code == 404
    assert client.post("/pedidos", json={"cliente_id": u["id"], "items": [
        {"producto_id": "nope", "cantidad": 1}]}).status_code == 404
    assert client.post("/pedidos", json={"cliente_id": u["id"], "items": []}).status_code == 422
    assert client.post("/pedidos", json={"cliente_id": u["id"], "items": [
        {"producto_id": p["id"], "cantidad": 0}]}).status_code == 422
    a = client.post("/usuarios", json={"nombre": "Ad", "email": "ad@mail.com",
                                       "tipo": "administrador"}).json()
    assert client.post("/pedidos", json={"cliente_id": a["id"], "items": [
        {"producto_id": p["id"], "cantidad": 1}]}).status_code == 403
    assert client.get("/usuarios/nope/pedidos").status_code == 404
