"""Esquemas Pydantic: validan las peticiones y definen las respuestas de la API."""
from datetime import datetime
from typing import Literal, Optional

from pydantic import BaseModel, ConfigDict, Field, model_validator

EMAIL_REGEX = r"^[^@\s]+@[^@\s]+\.[^@\s]+$"


# ------------------------------------------------------------------ 1.1 Usuario
class UsuarioCreate(BaseModel):
    model_config = ConfigDict(str_strip_whitespace=True)

    nombre: str = Field(..., min_length=1, max_length=100, examples=["Ana García"])
    email: str = Field(..., pattern=EMAIL_REGEX, examples=["ana@mail.com"])
    tipo: Literal["cliente", "administrador"]
    direccion_postal: Optional[str] = Field(None, max_length=200, examples=["Calle A"])

    @model_validator(mode="after")
    def cliente_necesita_direccion(self):
        if self.tipo == "cliente" and not self.direccion_postal:
            raise ValueError("Los clientes requieren 'direccion_postal'.")
        return self


class UsuarioRead(BaseModel):
    id: str
    nombre: str
    email: str
    es_admin: bool


# ----------------------------------------------------------------- 1.2 Producto
class ProductoCreate(BaseModel):
    model_config = ConfigDict(str_strip_whitespace=True)

    tipo: Literal["generico", "electronico", "ropa"]
    nombre: str = Field(..., min_length=1, max_length=100)
    precio: float = Field(..., gt=0)
    stock: int = Field(..., ge=0)
    # Solo electrónicos
    meses_garantia: Optional[int] = Field(None, ge=0)
    # Solo ropa
    talla: Optional[str] = Field(None, min_length=1)
    color: Optional[str] = Field(None, min_length=1)

    @model_validator(mode="after")
    def validar_atributos_por_tipo(self):
        if self.tipo == "electronico":
            if self.meses_garantia is None:
                raise ValueError("Los productos electrónicos requieren 'meses_garantia'.")
            if self.talla is not None or self.color is not None:
                raise ValueError("Un producto electrónico no admite 'talla' ni 'color'.")
        elif self.tipo == "ropa":
            if self.talla is None or self.color is None:
                raise ValueError("Los productos de ropa requieren 'talla' y 'color'.")
            if self.meses_garantia is not None:
                raise ValueError("Un producto de ropa no admite 'meses_garantia'.")
        else:  # generico
            if any(v is not None for v in (self.meses_garantia, self.talla, self.color)):
                raise ValueError(
                    "Un producto genérico no admite 'meses_garantia', 'talla' ni 'color'."
                )
        return self


class ProductoRead(BaseModel):
    id: str
    tipo: Literal["generico", "electronico", "ropa"]
    nombre: str
    precio: float
    stock: int
    meses_garantia: Optional[int] = None
    talla: Optional[str] = None
    color: Optional[str] = None


# ------------------------------------------------------------------ 1.3 Pedido
class PedidoItemCreate(BaseModel):
    producto_id: str
    cantidad: int = Field(..., gt=0)


class PedidoCreate(BaseModel):
    cliente_id: str
    items: list[PedidoItemCreate] = Field(..., min_length=1)


class PedidoItemRead(BaseModel):
    producto_id: str
    nombre: str
    precio_unitario: float
    cantidad: int
    subtotal: float


class PedidoRead(BaseModel):
    id: str
    fecha_pedido: datetime
    cliente: UsuarioRead
    total: float
    items: list[PedidoItemRead]
