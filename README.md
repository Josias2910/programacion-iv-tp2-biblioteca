# TP2 - Biblioteca

API con FastAPI, SQLModel y SQLite para administrar autores, libros, socios y préstamos.

## Ejecutar

Requiere Python 3.10 o superior. Desde esta carpeta:

```bash
python -m venv .venv
```

Activar el entorno:

```powershell
# Windows (PowerShell)
.venv\Scripts\Activate.ps1
```

```bash
# Linux / macOS
source .venv/bin/activate
```

```bash
python -m pip install -r requirements.txt
python -m uvicorn app.main:app --reload
```

Swagger: http://127.0.0.1:8000/docs

La base `biblioteca.db` se crea al iniciar. Los datos se conservan entre ejecuciones. Para cambiar su ubicación se puede definir `DATABASE_URL` con otra ruta SQLite.

## Uso

1. Crear un autor en `POST /autores`.
2. Crear un libro en `POST /libros` y asociarle autores en `POST /libros/{id}/autores/{autor_id}`.
3. Crear un socio en `POST /socios`.
4. Registrar un préstamo en `POST /prestamos` con `socio_id` y `libro_id`.
5. Devolverlo con `POST /prestamos/{id}/devolucion`.

Las fechas se toman del servidor. Cada préstamo vence a los 14 días y la multa es de $100 por día de atraso. Se descuentan y reponen las unidades disponibles al prestar y devolver.

Los tres catálogos tienen GET, POST, PUT y DELETE. PUT reemplaza los datos del recurso. Los filtros `disponibles=true` y `activos=true` muestran libros con stock y préstamos sin devolver. Con `false` muestran los casos contrarios; sin filtro se muestran todos.

No se eliminan libros o socios con préstamos registrados, para conservar el historial (409). Se puede desactivar un socio con PUT. Al borrar un autor se quitan sus asociaciones, no sus libros. El ISBN se trata como identificador único; no se valida su dígito de control. No se implementaron los roles opcionales.

## Tests

```bash
python -m pytest -q
```

Cada prueba utiliza una base independiente. Las pruebas de la API usan SQLite en memoria y no modifican `biblioteca.db`. Pytest muestra la cobertura y exige un mínimo del 80 %.
