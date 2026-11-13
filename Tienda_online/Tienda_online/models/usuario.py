import uuid

class Usuario:
    """Clase base para cualquier persona registrada en la tienda."""
    def __init__(self, nombre: str, email: str):
        self.id: str = str(uuid.uuid4())
        self.nombre: str = nombre
        self.email: str = email

    def is_admin(self) -> bool:
        """Por defecto, un usuario base no es administrador."""
        return False

    def __str__(self) -> str:
        return f"{self.nombre} ({self.email})"


class Cliente(Usuario):
    """Usuario de tipo cliente con dirección de envío."""
    def __init__(self, nombre: str, email: str, direccion_postal: str):
        super().__init__(nombre, email)
        self.direccion_postal: str = direccion_postal


class Administrador(Usuario):
    """Usuario con privilegios de gestión."""
    def __init__(self, nombre: str, email: str):
        super().__init__(nombre, email)

    def is_admin(self) -> bool:
        """Sobrescribe el método para confirmar que sí es administrador."""
        return True