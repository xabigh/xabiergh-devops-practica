import uuid

class Producto:
    """Clase base que representa un producto del catálogo."""
    def __init__(self, nombre: str, precio: float, stock: int):
        self.id: str = str(uuid.uuid4())
        self.nombre: str = nombre
        self.precio: float = precio
        self.stock: int = stock

    def hay_stock(self, cantidad: int) -> bool:
        """Comprueba si hay stock suficiente."""
        return self.stock >= cantidad

    def actualizar_stock(self, cantidad: int) -> None:
        """Suma o resta (con valores negativos) cantidad al stock."""
        self.stock += cantidad

    def __str__(self) -> str:
        return f"[{self.id}] {self.nombre} - {self.precio}€ (Stock: {self.stock})"


class ProductoElectronico(Producto):
    """Producto que incluye meses de garantía."""
    def __init__(self, nombre: str, precio: float, stock: int, meses_garantia: int):
        super().__init__(nombre, precio, stock)
        self.meses_garantia: int = meses_garantia

    def __str__(self) -> str:
        return super().__str__() + f" | Garantía: {self.meses_garantia} meses"


class ProductoRopa(Producto):
    """Producto textil con talla y color."""
    def __init__(self, nombre: str, precio: float, stock: int, talla: str, color: str):
        super().__init__(nombre, precio, stock)
        self.talla: str = talla
        self.color: str = color

    def __str__(self) -> str:
        return super().__str__() + f" | Talla: {self.talla}, Color: {self.color}"