# Documentación de Endpoints de la API - Sistema de Reserva de Hoteles

## API Gateway (Laravel) - Puerto 8000

| Método | Endpoint | Descripción | Requiere Auth |
| --- | --- | --- | --- |
| POST | `/api/register` | Registrar usuario (requiere pregunta y respuesta de seguridad) | No |
| POST | `/api/login` | Iniciar sesión y obtener el token | No |
| POST | `/api/forgot-password` | Enviar email para recibir la pregunta de seguridad | No |
| POST | `/api/reset-password` | Verificar respuesta y restablecer contraseña | No |
| POST | `/api/logout` | Revocar el token de acceso actual | Sí |
| GET | `/api/user` | Obtener el perfil del usuario autenticado | Sí |

### Flujo de Recuperación de Contraseña

**Paso 1** — Obtener la pregunta de seguridad:
```json
POST /api/forgot-password
{ "email": "usuario@correo.com" }

// Respuesta:
{ "email": "usuario@correo.com", "security_question": "¿Cuál es el nombre de tu mascota?" }
```

**Paso 2** — Responder la pregunta y cambiar la contraseña:
```json
POST /api/reset-password
{
  "email": "usuario@correo.com",
  "security_answer": "firulais",
  "new_password": "MiNuevaPassword123"
}
// Respuesta exitosa:
{ "message": "Contraseña actualizada correctamente." }
```

### Registro con Pregunta de Seguridad
```json
POST /api/register
{
  "username": "usuario1",
  "email": "usuario1@correo.com",
  "password": "Password123",
  "security_question": "¿Cuál es el nombre de tu mascota?",
  "security_answer": "firulais"
}
```

### Rutas con Proxy 

| Servicio | Endpoint | Ejemplo |
| --- | --- | --- |
| Hoteles | `/api/hotels/*` | `GET /api/hotels/` |
| Usuarios | `/api/users/*` | `GET /api/users/profile/` |
| Reservas | `/api/reservations/*` | `POST /api/reservations/` (Auth) |
| Pagos | `/api/payments/*` | `POST /api/payments/process` (Auth) |
| Reseñas | `/api/reviews/*` | `POST /api/reviews` |

---

## Microservicios Internos

### 1. MS Usuarios (Django) - Puerto 8001
- **POST** `/api/users/register/`: Crear usuario. Requiere `username`, `email`, `password`, `security_question` y `security_answer`.
- **POST** `/api/users/login/`: Validar credenciales (uso interno del Gateway).
- **GET** `/api/users/profile/`: Obtener detalles del usuario autenticado.
- **POST** `/api/users/forgot-password/`: Recibe el `email` del usuario y devuelve su pregunta de seguridad.
- **POST** `/api/users/reset-password/`: Recibe `email`, `security_answer` y `new_password`. Verifica la respuesta antes de actualizar.

### 2. MS Hoteles (Express) - Puerto 8002
- **GET** `/api/hotels`: Listar todos los hoteles desde Firestore.
- **POST** `/api/hotels`: Crear un nuevo hotel.
- **GET** `/api/hotels/:id`: Obtener detalles de un hotel específico.

### 3. MS Reservas (Flask) - Puerto 8003
- **POST** `/api/reservations`: Crear una nueva reserva.
- **GET** `/api/reservations/user/:id`: Listar reservas de un usuario específico.
- **PATCH** `/api/reservations/:id/status`: Actualizar el estado de una reserva.

### 4. MS Pagos (Express) - Puerto 8004
- **POST** `/api/payments/process`: Procesar un pago y guardarlo en PostgreSQL.

### 5. MS Reseñas (Flask) - Puerto 8005
- **POST** `/api/reviews`: Enviar una reseña para un hotel.
- **GET** `/api/reviews/hotel/:id`: Obtener todas las reseñas de un hotel.
