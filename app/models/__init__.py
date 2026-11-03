from datetime import date

from pydantic import EmailStr
from sqlmodel import Field, Relationship, SQLModel


class LibroAutor(SQLModel, table=True):
    libro_id: int = Field(foreign_key="libro.id", primary_key=True)
    autor_id: int = Field(foreign_key="autor.id", primary_key=True)


class AutorBase(SQLModel):
    nombre: str = Field(min_length=1, max_length=100)
    nacionalidad: str = Field(min_length=1, max_length=80)


class Autor(AutorBase, table=True):
    id: int | None = Field(default=None, primary_key=True)
    libros: list["Libro"] = Relationship(back_populates="autores", link_model=LibroAutor)


class AutorRead(AutorBase):
    id: int


class LibroBase(SQLModel):
    titulo: str = Field(min_length=1, max_length=200)
    isbn: str = Field(min_length=1, max_length=30)
    stock: int = Field(default=0, ge=0)
    anio: int = Field(ge=1)


class Libro(LibroBase, table=True):
    id: int | None = Field(default=None, primary_key=True)
    isbn: str = Field(unique=True, index=True)
    autores: list[Autor] = Relationship(back_populates="libros", link_model=LibroAutor)
    prestamos: list["Prestamo"] = Relationship(back_populates="libro")


class LibroRead(LibroBase):
    id: int
    autores: list[AutorRead] = Field(default_factory=list)


class SocioBase(SQLModel):
    nombre: str = Field(min_length=1, max_length=100)
    email: EmailStr
    activo: bool = True


class Socio(SQLModel, table=True):
    id: int | None = Field(default=None, primary_key=True)
    nombre: str
    email: str = Field(unique=True, index=True)
    activo: bool = True
    prestamos: list["Prestamo"] = Relationship(back_populates="socio")


class SocioRead(SocioBase):
    id: int


class PrestamoCreate(SQLModel):
    socio_id: int = Field(gt=0)
    libro_id: int = Field(gt=0)


class Prestamo(SQLModel, table=True):
    id: int | None = Field(default=None, primary_key=True)
    socio_id: int = Field(foreign_key="socio.id", index=True)
    libro_id: int = Field(foreign_key="libro.id", index=True)
    fecha_prestamo: date
    fecha_vencimiento: date
    fecha_devolucion: date | None = None
    multa: int = Field(default=0, ge=0)
    socio: Socio = Relationship(back_populates="prestamos")
    libro: Libro = Relationship(back_populates="prestamos")


class PrestamoRead(SQLModel):
    id: int
    socio_id: int
    libro_id: int
    fecha_prestamo: date
    fecha_vencimiento: date
    fecha_devolucion: date | None
    multa: int
