from models.usuario import Usuario, Cliente, Administrador
from models.producto import Producto
from models.pedido import Pedido
from services.excepciones import (
    UsuarioNoEncontrado,
    ProductoNoEncontrado,
    EmailYaRegistrado,
    TipoNoValido,
    UsuarioNoEsCliente,
    StockInsuficiente,
)


class TiendaService:
    """Clase mediadora que gestiona la lógica de la tienda online.

    Respecto a la Práctica 1, los errores ya no se imprimen por consola:
    se lanzan excepciones de dominio para que la API pueda devolver el
    código HTTP adecuado. Los métodos de consulta devuelven datos en lugar
    de imprimirlos.
    """

    def __init__(self):
        self.usuarios: dict[str, Usuario] = {}
        self.productos: dict[str, Producto] = {}
        self.pedidos: list[Pedido] = []

    # ------------------------------------------------------------------ usuarios
    def registrar_usuario(self, tipo: str, nombre: str, email: str,
                          direccion_postal: str = "") -> Usuario:
        """Registra un nuevo cliente o administrador."""
        if any(u.email.lower() == email.lower() for u in self.usuarios.values()):
            raise EmailYaRegistrado(f"El email '{email}' ya está registrado.")

        if tipo.lower() == "cliente":
            nuevo_usuario = Cliente(nombre, email, direccion_postal)
        elif tipo.lower() == "administrador":
            nuevo_usuario = Administrador(nombre, email)
        else:
            raise TipoNoValido(f"Tipo de usuario no válido: '{tipo}'.")

        self.usuarios[nuevo_usuario.id] = nuevo_usuario
        return nuevo_usuario

    def obtener_usuario(self, id_usuario: str) -> Usuario:
        if id_usuario not in self.usuarios:
            raise UsuarioNoEncontrado(f"Usuario {id_usuario} no encontrado.")
        return self.usuarios[id_usuario]

    def listar_usuarios(self) -> list[Usuario]:
        return list(self.usuarios.values())

    # ----------------------------------------------------------------- productos
    def anadir_producto(self, producto: Producto) -> Producto:
        """Guarda un producto en el inventario."""
        self.productos[producto.id] = producto
        return producto

    def obtener_producto(self, id_producto: str) -> Producto:
        if id_producto not in self.productos:
            raise ProductoNoEncontrado(f"Producto {id_producto} no encontrado.")
        return self.productos[id_producto]

    def eliminar_producto(self, id_producto: str) -> None:
        """Borra un producto del inventario si existe."""
        if id_producto not in self.productos:
            raise ProductoNoEncontrado(f"Producto {id_producto} no encontrado.")
        del self.productos[id_producto]

    def listar_productos(self) -> list[Producto]:
        return list(self.productos.values())

    # ------------------------------------------------------------------- pedidos
    def realizar_pedido(self, id_usuario: str,
                        solicitudes: list[tuple[str, int]]) -> Pedido:
        """Verifica usuario, productos y stock; descuenta unidades y crea el pedido."""
        usuario = self.obtener_usuario(id_usuario)
        if not isinstance(usuario, Cliente):
            raise UsuarioNoEsCliente("Solo los clientes pueden realizar pedidos.")

        # Agrupamos cantidades por producto: si el mismo producto aparece en
        # varias líneas, el stock se comprueba sobre la suma total.
        agrupadas: dict[str, int] = {}
        for id_prod, cantidad in solicitudes:
            agrupadas[id_prod] = agrupadas.get(id_prod, 0) + cantidad

        productos_a_comprar: list[tuple[Producto, int]] = []

        # 1. Comprobar que todos los productos existen y tienen stock suficiente
        for id_prod, cantidad in agrupadas.items():
            producto = self.obtener_producto(id_prod)
            if not producto.hay_stock(cantidad):
                raise StockInsuficiente(
                    f"Stock insuficiente para '{producto.nombre}' "
                    f"(disponible: {producto.stock}, solicitado: {cantidad})."
                )
            productos_a_comprar.append((producto, cantidad))

        # 2. Descontar el stock real (solo si todo lo anterior ha ido bien)
        for producto, cantidad in productos_a_comprar:
            producto.actualizar_stock(-cantidad)

        # 3. Registrar y devolver el pedido
        nuevo_pedido = Pedido(usuario, productos_a_comprar)
        self.pedidos.append(nuevo_pedido)
        return nuevo_pedido

    def listar_pedidos_usuario(self, id_usuario: str) -> list[Pedido]:
        """Devuelve los pedidos de un usuario ordenados por fecha."""
        self.obtener_usuario(id_usuario)
        pedidos_usuario = [p for p in self.pedidos if p.cliente.id == id_usuario]
        pedidos_usuario.sort(key=lambda p: p.fecha_pedido)
        return pedidos_usuario
