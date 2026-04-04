# Documentación de Endpoints — Sistema de Reserva de Hoteles

> **Versión**: Entrega #1 | **Base URL del Gateway**: `http://localhost:8000/api`

---

## Resumen de Servicios

| Servicio | Tecnología | Puerto | Base de Datos |
|---|---|---|---|
| API Gateway | Laravel| `8000` | MySQL |
| MS Usuarios | Django| `8001` | PostgreSQL |
| MS Hoteles | Express| `8002` | Cloud Firestore |
| MS Reservas | Flask| `8003` | MySQL |
| MS Pagos | Express| `8004` | PostgreSQL |
| MS Reseñas | Flask| `8005` | Cloud Firestore |

---

## 1. API Gateway (Laravel) — Puerto 8000

El Gateway es el **único punto de entrada** al sistema. 

### Autenticación

#### `POST /api/register`


- **Auth requerida**: No

**Body (JSON)**:
```json
{
  "username": "juanperez",
  "email": "juan@correo.com",
  "password": "Password123",
  "security_question": "¿Cuál es el nombre de tu mascota?",
  "security_answer": "firulais"
}
```

**Respuesta exitosa** `201 Created`:
```json
{
  "token": "1|abc123...",
  "user": {
    "id": 1,
    "username": "juanperez",
    "email": "juan@correo.com"
  }
}
```

**Errores**:
| Código | Descripción |
|---|---|
| `422` | Campos faltantes o email ya registrado |

---

#### `POST /api/login`
Autentica al usuario y devuelve un token de acceso Sanctum.

- **Auth requerida**: No

**Body (JSON)**:
```json
{
  "email": "juan@correo.com",
  "password": "Password123"
}
```

**Respuesta exitosa** `200 OK`:
```json
{
  "token": "2|xyz789...",
  "user": {
    "id": 1,
    "username": "juanperez",
    "email": "juan@correo.com"
  }
}
```

**Errores**:
| Código | Descripción |
|---|---|
| `401` | Credenciales inválidas |

---

#### `POST /api/logout`
Revoca el token de acceso actual del usuario.

- **Auth requerida**: Sí (`Bearer Token`)

**Respuesta exitosa** `200 OK`:
```json
{ "message": "Sesión cerrada correctamente." }
```

---

#### `GET /api/user`
Devuelve el perfil del usuario autenticado.

- **Auth requerida**: Sí (`Bearer Token`)

**Respuesta exitosa** `200 OK`:
```json
{
  "id": 1,
  "username": "juanperez",
  "email": "juan@correo.com"
}
```

---

### Recuperación de Contraseña

#### `POST /api/forgot-password`
**Paso 1**: Dado un email, devuelve la pregunta de seguridad del usuario.

- **Auth requerida**: No

**Body (JSON)**:
```json
{ "email": "juan@correo.com" }
```

**Respuesta exitosa** `200 OK`:
```json
{
  "email": "juan@correo.com",
  "security_question": "¿Cuál es el nombre de tu mascota?"
}
```

**Errores**:
| Código | Descripción |
|---|---|
| `404` | Email no encontrado |

---

#### `POST /api/reset-password`
**Paso 2**: Verifica la respuesta de seguridad y actualiza la contraseña.

- **Auth requerida**: No

**Body (JSON)**:
```json
{
  "email": "juan@correo.com",
  "security_answer": "firulais",
  "new_password": "NuevaPass456"
}
```

**Respuesta exitosa** `200 OK`:
```json
{ "message": "Contraseña actualizada correctamente." }
```

**Errores**:
| Código | Descripción |
|---|---|
| `401` | Respuesta de seguridad incorrecta |
| `404` | Usuario no encontrado |

---
### Rutas de Proxy
| Prefijo del Gateway | Microservicio destino | Auth |
|---|---|---|
| `/api/hotels/*` | MS Hoteles (`:8002`) | No |
| `/api/users/*` | MS Usuarios (`:8001`) | No |
| `/api/reservations/*` | MS Reservas (`:8003`) | **Sí** |
| `/api/payments/*` | MS Pagos (`:8004`) | **Sí** |
| `/api/reviews/*` | MS Reseñas (`:8005`) | No |

---

## 2. MS Usuarios (Django) — Puerto 8001

> Accesible públicamente via Gateway en `/api/users/*` o directamente en `http://localhost:8001/api/users/*`.

#### `POST /api/users/register/`
Crea un usuario en la base de datos PostgreSQL con su perfil de seguridad.

**Body (JSON)**:
```json
{
  "username": "juanperez",
  "email": "juan@correo.com",
  "password": "Password123",
  "security_question": "¿Cuál es el nombre de tu mascota?",
  "security_answer": "firulais"
}
```

**Respuesta exitosa** `201 Created`:
```json
{
  "id": 1,
  "username": "juanperez",
  "email": "juan@correo.com"
}
```

---

#### `POST /api/users/login/`
Valida credenciales. Uso **interno** del Gateway.

**Body (JSON)**:
```json
{ "email": "juan@correo.com", "password": "Password123" }
```

**Respuesta exitosa** `200 OK`:
```json
{
  "status": "OK",
  "user": { "id": 1, "username": "juanperez", "email": "juan@correo.com" }
}
```

**Errores**:
| Código | Descripción |
|---|---|
| `401` | Credenciales inválidas |

---

#### `GET /api/users/profile/`
Devuelve los datos del usuario autenticado vía token DRF.

- **Auth requerida**: Sí (Token DRF)

**Respuesta exitosa** `200 OK`:
```json
{ "id": 1, "username": "juanperez", "email": "juan@correo.com" }
```

---

#### `POST /api/users/forgot-password/`
**Body**: `{ "email": "juan@correo.com" }`

**Respuesta exitosa** `200 OK`:
```json
{
  "email": "juan@correo.com",
  "security_question": "¿Cuál es el nombre de tu mascota?"
}
```

---

#### `POST /api/users/reset-password/`
**Body**:
```json
{
  "email": "juan@correo.com",
  "security_answer": "firulais",
  "new_password": "NuevaPass456"
}
```

**Respuesta exitosa** `200 OK`:
```json
{ "message": "Contraseña actualizada correctamente." }
```

---

## 3. MS Hoteles (Express/Node.js) — Puerto 8002

> Accesible via Gateway en `/api/hotels/*`. Almacena datos en **Cloud Firestore**.

#### `GET /api/hotels`
Lista todos los hoteles. Acepta filtro por ciudad.

**Query params (opcionales)**:
| Parámetro | Tipo | Descripción |
|---|---|---|
| `city` | string | Filtra hoteles por ciudad |

**Ejemplo**: `GET /api/hotels?city=Bogotá`

**Respuesta exitosa** `200 OK`:
```json
[
  {
    "id": "abc123",
    "name": "Hotel El Dorado",
    "city": "Bogotá",
    "price_per_night": 250000,
    "rating": 4.5
  }
]
```

---

#### `POST /api/hotels`
Crea un nuevo hotel en Firestore.

**Body (JSON)**:
```json
{
  "name": "Hotel El Dorado",
  "city": "Bogotá",
  "price_per_night": 250000,
  "rating": 4.5,
  "description": "Hotel en el centro histórico."
}
```

**Respuesta exitosa** `201 Created`:
```json
{ "id": "newFirestoreId", "name": "Hotel El Dorado", "city": "Bogotá", ... }
```

---

#### `GET /api/hotels/:id`
Obtiene los detalles de un hotel específico por su ID de Firestore.

**Respuesta exitosa** `200 OK`:
```json
{ "id": "abc123", "name": "Hotel El Dorado", "city": "Bogotá", ... }
```

**Errores**:
| Código | Descripción |
|---|---|
| `404` | Hotel no encontrado |

---

#### `PUT /api/hotels/:id`
Actualiza los campos de un hotel existente.

**Body (JSON)** _(campos a actualizar)_:
```json
{ "price_per_night": 280000, "rating": 4.8 }
```

**Respuesta exitosa** `200 OK`:
```json
{ "id": "abc123", "price_per_night": 280000, "rating": 4.8 }
```

---

#### `DELETE /api/hotels/:id`
Elimina un hotel de Firestore.

**Respuesta exitosa** `200 OK`:
```json
{ "message": "Hotel deleted" }
```

---

## 4. MS Reservas (Flask/Python) — Puerto 8003

> Accesible via Gateway en `/api/reservations/*` (**requiere Auth**). Almacena en **MySQL**.

#### `POST /api/reservations`
Crea una nueva reserva. Verifica que no haya solapamiento de fechas para el mismo hotel.

**Body (JSON)**:
```json
{
  "user_id": 1,
  "hotel_id": "abc123",
  "check_in": "2026-05-10",
  "check_out": "2026-05-15"
}
```

**Respuesta exitosa** `201 Created`:
```json
{
  "id": 42,
  "user_id": 1,
  "hotel_id": "abc123",
  "status": "pending"
}
```

**Errores**:
| Código | Descripción |
|---|---|
| `400` | Hotel no disponible para esas fechas |

---

#### `GET /api/reservations/user/:user_id`
Lista todas las reservas de un usuario.

**Respuesta exitosa** `200 OK`:
```json
[
  {
    "id": 42,
    "hotel_id": "abc123",
    "check_in": "2026-05-10",
    "check_out": "2026-05-15",
    "status": "confirmed"
  }
]
```

---

#### `PATCH /api/reservations/:id/status`
Actualiza el estado de una reserva. Utilizado internamente por el MS Pagos.

**Body (JSON)**:
```json
{ "status": "confirmed" }
```
> **Estados válidos**: `pending` | `confirmed` | `canceled`

**Respuesta exitosa** `200 OK`:
```json
{ "id": 42, "status": "confirmed" }
```

**Errores**:
| Código | Descripción |
|---|---|
| `404` | Reserva no encontrada |

---

## 5. MS Pagos (Express/Node.js) — Puerto 8004

> Accesible via Gateway en `/api/payments/*` (**requiere Auth**). Almacena en **PostgreSQL**.

#### `POST /api/payments/process`
Procesa un pago para una reserva. Si el pago es exitoso, notifica al MS Reservas para confirmar la reserva automáticamente.

**Body (JSON)**:
```json
{
  "reservation_id": 42,
  "amount": 1250000
}
```

**Respuesta exitosa** `201 Created`:
```json
{
  "message": "Payment processed and reservation confirmed",
  "transaction": {
    "id": 7,
    "reservation_id": 42,
    "amount": "1250000.00",
    "status": "success",
    "created_at": "2026-05-10T14:30:00Z"
  }
}
```

**Errores**:
| Código | Descripción |
|---|---|
| `400` | Pago rechazado (simulación ~5% de fallos) |
| `500` | Error interno (ej. MS Reservas no disponible) |

---

## 6. MS Reseñas (Flask/Python) — Puerto 8005

> Accesible via Gateway en `/api/reviews/*`. Almacena en **Cloud Firestore**.

#### `POST /api/reviews`
Publica una reseña sobre un hotel. El `rating` debe estar entre 1 y 5.

**Body (JSON)**:
```json
{
  "hotel_id": "abc123",
  "user_id": 1,
  "rating": 5,
  "comment": "Excelente hotel, muy recomendado."
}
```

**Respuesta exitosa** `201 Created`:
```json
{
  "id": "firestoreDocId",
  "hotel_id": "abc123",
  "user_id": 1,
  "rating": 5,
  "comment": "Excelente hotel, muy recomendado."
}
```

**Errores**:
| Código | Descripción |
|---|---|
| `400` | Rating fuera del rango 1–5 |

---

#### `GET /api/reviews/hotel/:hotel_id`
Obtiene todas las reseñas de un hotel específico.

**Respuesta exitosa** `200 OK`:
```json
[
  {
    "id": "firestoreDocId",
    "hotel_id": "abc123",
    "user_id": 1,
    "rating": 5,
    "comment": "Excelente hotel, muy recomendado."
  }
]
```

---

#### `GET /api/reviews/user/:user_id`
Obtiene todas las reseñas escritas por un usuario específico.

**Respuesta exitosa** `200 OK`:
```json
[
  {
    "id": "firestoreDocId2",
    "hotel_id": "xyz789",
    "user_id": 1,
    "rating": 4,
    "comment": "Muy buena atención."
  }
]
```
