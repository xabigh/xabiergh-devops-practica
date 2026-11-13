"""Punto de entrada y capa de exposición (API REST con FastAPI).

Ejecutar:  uvicorn main:app --reload
Docs:      http://127.0.0.1:8000/docs
"""
from fastapi import FastAPI, Request, status
from fastapi.responses import JSONResponse

from models.producto import Producto, ProductoElectronico, ProductoRopa
from models.usuario import Usuario
from models.pedido import Pedido
from schemas import (
    UsuarioCreate, UsuarioRead,
    ProductoCreate, ProductoRead,
    PedidoCreate, PedidoRead, PedidoItemRead,
)
from services.excepciones import (
    TiendaError, UsuarioNoEncontrado, ProductoNoEncontrado, EmailYaRegistrado,
    TipoNoValido, UsuarioNoEsCliente, StockInsuficiente,
)
from services.tienda_service import TiendaService

app = FastAPI(
    title="Tienda online API",
    description="API REST de la tienda online (Práctica 3).",
    version="1.0.0",
)

tienda = TiendaService()


# ------------------------------------------------- errores de dominio -> HTTP
# Todas las respuestas de error usan el mismo formato: {"detail": "..."}
ESTADO_POR_ERROR: dict[type[TiendaError], int] = {
    UsuarioNoEncontrado: status.HTTP_404_NOT_FOUND,
    ProductoNoEncontrado: status.HTTP_404_NOT_FOUND,
    EmailYaRegistrado: status.HTTP_409_CONFLICT,
    StockInsuficiente: status.HTTP_409_CONFLICT,
    UsuarioNoEsCliente: status.HTTP_403_FORBIDDEN,
    TipoNoValido: 422,
}


@app.exception_handler(TiendaError)
async def manejar_error_tienda(_: Request, exc: TiendaError):
    codigo = ESTADO_POR_ERROR.get(type(exc), status.HTTP_400_BAD_REQUEST)
    return JSONResponse(status_code=codigo, content={"detail": str(exc)})


# ------------------------------------------- conversión dominio -> esquemas
def usuario_a_read(u: Usuario) -> UsuarioRead:
    return UsuarioRead(id=u.id, nombre=u.nombre, email=u.email, es_admin=u.is_admin())


def producto_a_read(p: Producto) -> ProductoRead:
    datos = dict(id=p.id, nombre=p.nombre, precio=p.precio, stock=p.stock)
    if isinstance(p, ProductoElectronico):
        return ProductoRead(tipo="electronico", meses_garantia=p.meses_garantia, **datos)
    if isinstance(p, ProductoRopa):
        return ProductoRead(tipo="ropa", talla=p.talla, color=p.color, **datos)
    return ProductoRead(tipo="generico", **datos)


def pedido_a_read(p: Pedido) -> PedidoRead:
    items = [
        PedidoItemRead(
            producto_id=prod.id,
            nombre=prod.nombre,
            precio_unitario=prod.precio,
            cantidad=cant,
            subtotal=round(prod.precio * cant, 2),
        )
        for prod, cant in p.productos_cantidades
    ]
    return PedidoRead(
        id=p.id,
        fecha_pedido=p.fecha_pedido,
        cliente=usuario_a_read(p.cliente),
        total=round(p.calcular_total(), 2),
        items=items,
    )


# ------------------------------------------------------------------ Usuarios
@app.post("/usuarios", response_model=UsuarioRead,
          status_code=status.HTTP_201_CREATED, tags=["Usuarios"])
def crear_usuario(datos: UsuarioCreate):
    usuario = tienda.registrar_usuario(
        datos.tipo, datos.nombre, datos.email, datos.direccion_postal or ""
    )
    return usuario_a_read(usuario)


@app.get("/usuarios", response_model=list[UsuarioRead], tags=["Usuarios"])
def listar_usuarios():
    return [usuario_a_read(u) for u in tienda.listar_usuarios()]


@app.get("/usuarios/{usuario_id}", response_model=UsuarioRead, tags=["Usuarios"])
def obtener_usuario(usuario_id: str):
    return usuario_a_read(tienda.obtener_usuario(usuario_id))


# ----------------------------------------------------------------- Productos
@app.post("/productos", response_model=ProductoRead,
          status_code=status.HTTP_201_CREATED, tags=["Productos"])
def crear_producto(datos: ProductoCreate):
    if datos.tipo == "electronico":
        producto = ProductoElectronico(datos.nombre, datos.precio, datos.stock,
                                       datos.meses_garantia)
    elif datos.tipo == "ropa":
        producto = ProductoRopa(datos.nombre, datos.precio, datos.stock,
                                datos.talla, datos.color)
    else:
        producto = Producto(datos.nombre, datos.precio, datos.stock)
    tienda.anadir_producto(producto)
    return producto_a_read(producto)


@app.get("/productos", response_model=list[ProductoRead], tags=["Productos"])
def listar_productos():
    return [producto_a_read(p) for p in tienda.listar_productos()]


@app.get("/productos/{producto_id}", response_model=ProductoRead, tags=["Productos"])
def obtener_producto(producto_id: str):
    return producto_a_read(tienda.obtener_producto(producto_id))


@app.delete("/productos/{producto_id}", status_code=status.HTTP_204_NO_CONTENT,
            tags=["Productos"])
def eliminar_producto(producto_id: str):
    tienda.eliminar_producto(producto_id)


# ------------------------------------------------------------------- Pedidos
@app.post("/pedidos", response_model=PedidoRead,
          status_code=status.HTTP_201_CREATED, tags=["Pedidos"])
def crear_pedido(datos: PedidoCreate):
    solicitudes = [(i.producto_id, i.cantidad) for i in datos.items]
    pedido = tienda.realizar_pedido(datos.cliente_id, solicitudes)
    return pedido_a_read(pedido)


@app.get("/usuarios/{cliente_id}/pedidos", response_model=list[PedidoRead],
         tags=["Pedidos"])
def listar_pedidos_cliente(cliente_id: str):
    return [pedido_a_read(p) for p in tienda.listar_pedidos_usuario(cliente_id)]
