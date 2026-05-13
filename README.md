# Sistema de Reserva de Hoteles — Arquitectura de Microservicios

Este proyecto es una plataforma de reserva de hoteles basada en una arquitectura de microservicios, utilizando tecnologías como Laravel, Django, Flask y Express, con bases de datos SQL y NoSQL.

---

## 📋 Requisitos Previos

Asegúrate de tener instalado:

| Herramienta | Versión mínima | Propósito |
|---|---|---|
| **Docker & Compose** | 20.10+ | Despliegue orquestado (Recomendado) |
| PHP + Composer | 8.1+ | API Gateway (Laravel) |
| Python + pip | 3.10+ | MS Usuarios, Reservas, Reseñas |
| Node.js + npm | 18+ | MS Hoteles, Pagos |
| MySQL | 8.0+ | API Gateway, MS Reservas |
| PostgreSQL | 15+ | MS Usuarios, MS Pagos |

---

## 🐳 Despliegue con Docker (Recomendado)

La forma más rápida de iniciar todo el ecosistema es utilizando Docker Compose.

### 0. Configuración Inicial (¡Importante!)
Antes de levantar los contenedores, debes configurar las credenciales secretas que no están incluidas en el repositorio por seguridad:
1. Pide al administrador las credenciales de Firebase o usa unas propias.
2. Coloca la llave para el MS Hoteles en: `Hoteles_express/serviceAccountKey.json`.
3. Coloca la llave para el MS Reseñas en: `Reseñas_flask/config/firebase-key.json`.
4. Copia los archivos `.env.example` y renómbralos a `.env` en los servicios correspondientes (`Api_gatewey_laravel`, `Pagos_express`, `Reseñas_flask`).

### 1. Construir e Iniciar Contenedores
Desde la raíz del proyecto:
```bash
docker-compose up --build -d
```

### 2. Verificar Estado
```bash
docker-compose ps
```

### 3. Ver Logs
```bash
docker-compose logs -f [nombre_del_servicio]
```

### Servicios Disponibles (Docker)
| Servicio | URL Local | Puerto |
|---|---|---|
| **API Gateway** | `http://localhost:8000` | 8000 |
| **MS Usuarios** | `http://localhost:8001` | 8001 |
| **MS Hoteles** | `http://localhost:8002` | 8002 |
| **MS Reservas** | `http://localhost:8003` | 8003 |
| **MS Pagos** | `http://localhost:8004` | 8004 |
| **MS Reseñas** | `http://localhost:8005` | 8005 |

---

## 🚀 Instrucciones de Despliegue Local (Manual)

Si prefieres ejecutar los servicios individualmente sin Docker:

### Paso 1 — Clonar el Repositorio
```bash
git clone https://github.com/yllano/Reserva_hoteles.git
cd Reserva_hoteles
```

### Paso 2 — Configurar Servicios
Cada microservicio requiere su propia configuración. Consulta los archivos `.env` o `settings.py` en cada carpeta:
1. **Gateway (8000)**: `composer install && cp .env.example .env && php artisan key:generate && php artisan serve`
2. **Usuarios (8001)**: `pip install -r requirements.txt && python manage.py migrate && python manage.py runserver 8001`
3. **Hoteles (8002)**: `npm install && node index.js` (Requiere `serviceAccountKey.json`)
4. **Reservas (8003)**: `pip install -r requirements.txt && python app.py`
5. **Pagos (8004)**: `npm install && node index.js`
6. **Reseñas (8005)**: `pip install -r requirements.txt && python app.py`

---

## 🧪 Pruebas (Testing)

El sistema cuenta con pruebas automatizadas para asegurar la integridad y el rendimiento de los microservicios.

### 1. Pruebas Unitarias e Integración (MS Reservas)
Validan la lógica de negocio, manejo de fechas y estados de reserva en Flask.

*   **Archivo**: `tests/test_reservas.py`
*   **Ejecución**:
    ```bash
    python tests/test_reservas.py
    ```
*   **Endpoints Probados**:
    *   `POST /api/reservations`: Creación exitosa, validación de campos y control de solapamiento de fechas.
    *   `GET /api/reservations/user/<user_id>`: Listado de reservas por usuario y aislamiento de datos.
    *   `PATCH /api/reservations/<id>/status`: Cambio de estados (`pending`, `confirmed`, `canceled`).

### 2. Pruebas de Rendimiento y Estrés (Locust)
Simulan tráfico masivo para identificar cuellos de botella en el procesamiento de pagos.

*   **Archivo**: `tests/locustfile.py`
*   **Ejecución**:
    ```bash
    locust -f tests/locustfile.py --host=http://localhost:8004
    ```
*   **Endpoints Probados (MS Pagos)**:
    *   `POST /api/payments/process`: Procesamiento de pagos con distintos montos, validación de errores de concurrencia y ráfagas de tráfico.
    *   `GET /api/payments`: Verificación de rutas de consulta.

---

## 🔑 Variables de Entorno y Configuración

| Servicio | Configuración Clave |
|---|---|
| **Bases de Datos** | Se inicializan automáticamente vía `init-db.sql` en Docker. |
| **Firebase** | Los MS de Hoteles y Reseñas requieren llaves de servicio en sus carpetas `config/`. |
| **API Gateway** | Gestiona el ruteo interno hacia `http://[service_name]:[port]`. |

---

## 📄 Documentación Adicional
*   **Arquitectura Detallada**: [ARCHITECTURE.md](ARCHITECTURE.md)
*   **Catálogo de Endpoints**: [DOCS/ENDPOINTS.md](DOCS/ENDPOINTS.md)
*   **Reporte de Rendimiento**: [DOCS/PERFORMANCE_REPORT.md](DOCS/PERFORMANCE_REPORT.md)

