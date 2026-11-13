"""Excepciones de dominio. La capa API (main.py) las traduce a códigos HTTP."""


class TiendaError(Exception):
    """Clase base de los errores de negocio de la tienda."""


class UsuarioNoEncontrado(TiendaError):
    pass


class ProductoNoEncontrado(TiendaError):
    pass


class EmailYaRegistrado(TiendaError):
    pass


class TipoNoValido(TiendaError):
    pass


class UsuarioNoEsCliente(TiendaError):
    pass


class StockInsuficiente(TiendaError):
    pass
