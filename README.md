# Sistema de Reserva de Hoteles — Arquitectura de Microservicios

Sistema distribuido compuesto por seis microservicios que implementa autenticación, gestión de hoteles, reservas, pagos y reseñas, con un API Gateway como único punto de entrada.

## 🏗️ Arquitectura

| Servicio | Tecnología | Puerto | Base de Datos |
|---|---|---|---|
| API Gateway | Laravel (PHP) | `8000` | MySQL |
| MS Usuarios | Django (Python) | `8001` | PostgreSQL |
| MS Hoteles | Express (Node.js) | `8002` | Cloud Firestore |
| MS Reservas | Flask (Python) | `8003` | MySQL |
| MS Pagos | Express (Node.js) | `8004` | PostgreSQL |
| MS Reseñas | Flask (Python) | `8005` | Cloud Firestore |

Para el diagrama completo, consulta [ARCHITECTURE.md](ARCHITECTURE.md).

---

## ✅ Requisitos Previos

Asegúrate de tener instalado:

| Herramienta | Versión mínima | Usado por |
|---|---|---|
| PHP + Composer | 8.1+ | API Gateway (Laravel) |
| Python + pip | 3.10+ | MS Usuarios, MS Reservas, MS Reseñas |
| Node.js + npm | 18+ | MS Hoteles, MS Pagos |
| MySQL | 8.0+ | API Gateway, MS Reservas |
| PostgreSQL | 14+ | MS Usuarios, MS Pagos |
| Proyecto Firebase | — | MS Hoteles, MS Reseñas (Firestore) |

---

## 🚀 Instrucciones de Despliegue Local

### Paso 1 — Clonar el Repositorio

```bash
git clone https://github.com/yllano/Reserva_hoteles.git
cd Reserva_hoteles
```

### Paso 2 — Configurar el API Gateway (Laravel) — Puerto 8000

```bash
cd Api_gatewey_laravel
composer install
cp .env.example .env
```

Edita el archivo `.env` con tus credenciales de MySQL:
```env
DB_CONNECTION=mysql
DB_HOST=127.0.0.1
DB_PORT=3306
DB_DATABASE=reserva_hotel
DB_USERNAME=root
DB_PASSWORD=tu_password
```

```bash
php artisan key:generate
php artisan migrate
php artisan serve --port=8000
```

### Paso 3 — Configurar MS Usuarios (Django) — Puerto 8001

```bash
cd ../Usuarios_django
pip install -r requirements.txt
```

Edita `Usuarios_django/settings.py` con tus credenciales de PostgreSQL:
```python
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': 'usuarios_db',
        'USER': 'postgres',
        'PASSWORD': 'tu_password',
        'HOST': 'localhost',
        'PORT': '5432',
    }
}
```

```bash
python manage.py migrate
python manage.py runserver 8001
```

### Paso 4 — Configurar MS Hoteles (Express) — Puerto 8002

Requiere un archivo `serviceAccountKey.json` de Firebase en la raíz del servicio.

```bash
cd ../Hoteles_express
npm install
node index.js
```
> El servicio inicia en el puerto `8002`.

### Paso 5 — Configurar MS Reservas (Flask) — Puerto 8003

```bash
cd ../Reservas_flask
pip install flask flask-sqlalchemy flask-cors mysql-connector-python
```

Edita la cadena de conexión en `app.py`:
```python
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+mysqlconnector://root:tu_password@localhost/reserva_hotel'
```

```bash
python app.py
```
> El servicio inicia en el puerto `8003`.

### Paso 6 — Configurar MS Pagos (Express) — Puerto 8004

```bash
cd ../Pagos_express
npm install
```

Edita el archivo `.env` con tus credenciales de PostgreSQL:
```env
PGUSER=postgres
PGPASSWORD=tu_password
PGDATABASE=pagos_db
PGHOST=localhost
PGPORT=5432
```

```bash
node index.js
```
> El servicio inicia en el puerto `8004`.

### Paso 7 — Configurar MS Reseñas (Flask) — Puerto 8005

Requiere colocar el archivo de credenciales de Firebase en `Reseñas_flask/config/firebase-key.json`.

```bash
cd ../Reseñas_flask
pip install flask flask-cors google-cloud-firestore
python app.py
```
> El servicio inicia en el puerto `8005`.

---

## 🔑 Variables de Entorno — Resumen

| Servicio | Archivo | Variable clave |
|---|---|---|
| API Gateway | `.env` | `DB_DATABASE`, `DB_USERNAME`, `DB_PASSWORD` |
| MS Usuarios | `settings.py` | `DATABASES → NAME, USER, PASSWORD` |
| MS Hoteles | `serviceAccountKey.json` | Credenciales Firebase |
| MS Reservas | `app.py` | `SQLALCHEMY_DATABASE_URI` |
| MS Pagos | `.env` | `PGUSER`, `PGPASSWORD`, `PGDATABASE` |
| MS Reseñas | `config/firebase-key.json` | Credenciales Firebase |

---

## 📄 Documentación de la API

Lista completa de endpoints con cuerpos de petición y respuesta: [DOCS/ENDPOINTS.md](DOCS/ENDPOINTS.md)

## 📈 Pruebas de Rendimiento

### Ejecutar las pruebas automatizadas

```bash
# Desde la raíz del proyecto
pip install requests
python tests/performance_test.py
```

Los resultados se guardan automáticamente en `tests/results/performance_results_<timestamp>.json`.

El informe de resultados de la Entrega #1 está en [DOCS/PERFORMANCE_REPORT.md](DOCS/PERFORMANCE_REPORT.md).
