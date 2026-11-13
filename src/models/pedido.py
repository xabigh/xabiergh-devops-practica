import uuid
from datetime import datetime
from models.usuario import Cliente
from models.producto import Producto

class Pedido:
    """Representa una compra realizada por un cliente."""
    def __init__(self, cliente: Cliente, productos_cantidades: list[tuple[Producto, int]]):
        self.id: str = str(uuid.uuid4())
        self.cliente: Cliente = cliente
        self.productos_cantidades: list[tuple[Producto, int]] = productos_cantidades
        self.fecha_pedido: datetime = datetime.now()

    def calcular_total(self) -> float:
        """Suma el precio de cada producto multiplicado por su cantidad solicitada."""
        total = 0.0
        for producto, cantidad in self.productos_cantidades:
            total += producto.precio * cantidad
        return total

    def __str__(self) -> str:
        resumen = f"\nPedido ID: {self.id}\n"
        resumen += f"Cliente: {self.cliente.nombre} | Fecha: {self.fecha_pedido.strftime('%d/%m/%Y %H:%M:%S')}\n"
        resumen += "Productos:\n"
        for producto, cantidad in self.productos_cantidades:
            resumen += f"  - {producto.nombre} x {cantidad} unid. ({producto.precio * cantidad:.2f}€)\n"
        resumen += f"TOTAL A PAGAR: {self.calcular_total():.2f}€\n"
        return resumen