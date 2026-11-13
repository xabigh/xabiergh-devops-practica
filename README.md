## Docker

Requisitos: tener [Docker](https://www.docker.com/) instalado y en ejecución.

### a) Construir la imagen

Desde la raíz del repositorio (donde está el `Dockerfile`):

```bash
docker build -t xabiergh-devops-practica:1.0 .
```

- `-t nombre:etiqueta` pone nombre y versión a la imagen.
- El `.` indica que el contexto de construcción es la carpeta actual.
- La imagen parte de `python:3.12-slim`, instala las dependencias de `requirements.txt` y ejecuta la app con un usuario sin privilegios (`appuser`).
- `.dockerignore` excluye `.git`, entornos virtuales, caches y tests para mantener la imagen ligera.

Comprobar que existe:

```bash
docker images xabiergh-devops-practica
```

### b) Ejecutar el contenedor

Ejecución básica (se elimina al parar con `Ctrl+C`):

```bash
docker run --rm -p 8000:8000 xabiergh-devops-practica:1.0
```

En segundo plano y con nombre:

```bash
docker run -d --name tienda-api -p 8000:8000 xabiergh-devops-practica:1.0
docker logs tienda-api      # ver la salida
docker stop tienda-api      # parar
docker rm tienda-api        # eliminar
```

Usando otro puerto del equipo (por ejemplo 9000, la API sigue en el 8000 dentro del contenedor):

```bash
docker run --rm -p 9000:8000 xabiergh-devops-practica:1.0
```

### c) Variables de entorno

La aplicación no lee ninguna variable de entorno, por lo que no es necesario pasar `-e` ni `--env-file`. El único parámetro configurable al ejecutar es el puerto del equipo, mediante `-p PUERTO_EQUIPO:8000`. No se incluyen secretos en la imagen ni en el repositorio.

### d) Salida esperada y pasos de prueba

**1. Salida al arrancar**

```
INFO:     Started server process [1]
INFO:     Waiting for application startup.
INFO:     Application startup complete.
INFO:     Uvicorn running on http://0.0.0.0:8000 (Press CTRL+C to quit)
```

**2. Documentación interactiva**

- Swagger UI: http://localhost:8000/docs
- Esquema OpenAPI: http://localhost:8000/openapi.json

**3. Endpoints disponibles**

| Método | Ruta | Descripción |
|--------|------|-------------|
| GET | /usuarios | Listar usuarios |
| POST | /usuarios | Crear usuario |
| GET | /usuarios/{usuario_id} | Obtener un usuario |
| GET | /productos | Listar productos |
| POST | /productos | Crear producto |
| GET | /productos/{producto_id} | Obtener un producto |
| DELETE | /productos/{producto_id} | Eliminar un producto |
| POST | /pedidos | Crear pedido |
| GET | /usuarios/{cliente_id}/pedidos | Listar pedidos de un cliente |

**4. Pasos de prueba**

1. Listar usuarios (al inicio debe devolver la lista vacía o la inicial):

```bash
curl http://localhost:8000/usuarios
```

2. Crear un usuario desde `/docs`: abre `POST /usuarios`, pulsa **Try it out**, edita el JSON de ejemplo y pulsa **Execute**. Debe responder con el código `200` o `201` y el usuario creado.
3. Repetir `GET /usuarios`: debe incluir el usuario creado.
4. Crear un producto con `POST /productos` y comprobarlo con `GET /productos`.
5. Crear un pedido con `POST /pedidos` usando los ids del usuario y del producto, y comprobarlo con `GET /usuarios/{cliente_id}/pedidos`.
6. Probar un id inexistente, por ejemplo `curl -i http://localhost:8000/productos/9999`: debe devolver un error `404`.

### Descargar la imagen publicada (pull)

```bash
docker pull TU_USUARIO_DOCKERHUB/xabiergh-devops-practica:1.0
docker run --rm -p 8000:8000 TU_USUARIO_DOCKERHUB/xabiergh-devops-practica:1.0
```